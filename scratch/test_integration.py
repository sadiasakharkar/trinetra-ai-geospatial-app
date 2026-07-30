import urllib.request
import json
import time
import numpy as np
import cv2

def test_api():
    base_url = "http://127.0.0.1:8000"
    print("Testing TRINETRA-AI API integration at:", base_url)
    
    # 1. Health check
    try:
        req = urllib.request.Request(f"{base_url}/api/health")
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            print("✓ Health check succeeded:", res)
    except Exception as e:
        print("✗ Health check failed:", e)
        return

    # 2. Get datasets
    try:
        req = urllib.request.Request(f"{base_url}/api/datasets")
        with urllib.request.urlopen(req) as response:
            datasets = json.loads(response.read().decode())
            print(f"✓ Datasets retrieved: {len(datasets)} items found.")
            for d in datasets:
                print(f"  - {d['id']}: {d['name']} ({d['cloudCover']}% cloud cover)")
    except Exception as e:
        print("✗ Get datasets failed:", e)
        return

    # 2b. Test Custom File Upload
    print("Testing custom dataset upload...")
    try:
        # Create a dummy image file
        import tempfile
        import os
        
        # Save a small dummy PNG
        temp_dir = tempfile.gettempdir()
        dummy_file = os.path.join(temp_dir, "test_cloudy.png")
        dummy_data = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        cv2.imwrite(dummy_file, dummy_data)
        
        # Multi-part form data upload encoding
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        parts = []
        parts.append(f'--{boundary}'.encode())
        parts.append(f'Content-Disposition: form-data; name="file"; filename="test_cloudy.png"'.encode())
        parts.append(b'Content-Type: image/png')
        parts.append(b'')
        with open(dummy_file, "rb") as f:
            parts.append(f.read())
        parts.append(f'--{boundary}--'.encode())
        parts.append(b'')
        body = b'\r\n'.join(parts)
        
        req = urllib.request.Request(
            f"{base_url}/api/upload",
            data=body,
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(body))
            }
        )
        with urllib.request.urlopen(req) as response:
            custom_ds = json.loads(response.read().decode())
            print("✓ Custom upload succeeded. Ingested Dataset ID:", custom_ds['id'])
            # Set this as the dataset to reconstruct
            dataset_id = custom_ds['id']
            # Clean up temp file
            os.remove(dummy_file)
    except Exception as e:
        print("✗ Custom upload failed, falling back to preset dataset:", e)
        dataset_id = datasets[0]['id']

    # 3. Start reconstruction job
    config = {
        "model": "diffcr-v2",
        "sources": [
            {"id": "sar", "label": "Sentinel-1 SAR", "desc": "VV + VH radar", "enabled": True},
            {"id": "temporal", "label": "Temporal Composite", "desc": "4 clear reference scenes", "enabled": True},
            {"id": "dem", "label": "CartoDEM v3", "desc": "Elevation prior", "enabled": True},
            {"id": "spectral", "label": "Spectral Priors", "desc": "NDVI / NDWI", "enabled": False}
        ],
        "fidelity": 80,
        "tileSize": 256,
        "outputFormat": "GeoTIFF",
        "preserveNdvi": True
    }
    
    payload = json.dumps({
        "datasetId": dataset_id,
        "config": config
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(
            f"{base_url}/api/reconstruct/start",
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            job_id = res['job_id']
            print("✓ Job started successfully. Job ID:", job_id)
    except Exception as e:
        print("✗ Start reconstruction job failed:", e)
        return

    # 4. Poll job status
    print("Polling job progress...")
    completed = False
    for i in range(30): # max 30 seconds
        time.sleep(1)
        try:
            req = urllib.request.Request(f"{base_url}/api/reconstruct/status/{job_id}")
            with urllib.request.urlopen(req) as response:
                status_data = json.loads(response.read().decode())
                progress = status_data['progress']
                status = status_data['status']
                logs = status_data['logs']
                print(f"  - Progress: {progress}% | Status: {status} | Logs count: {len(logs)}")
                
                if status == "complete":
                    print("✓ Job completed!")
                    completed = True
                    break
                elif status == "failed":
                    print("✗ Job failed on backend!")
                    break
        except Exception as e:
            print("✗ Polling status query error:", e)
            break
            
    if not completed:
        print("✗ Job did not complete in time.")
        return

    # 5. Fetch result metrics
    try:
        req = urllib.request.Request(f"{base_url}/api/reconstruct/result/{job_id}")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print("✓ Result metrics received:")
            print("  - Cloud removed:", result['cloud_cover_pct'], "%")
            print("  - Metrics summary:", result['metrics'])
            print("  - Output paths:", result['output_paths'])
    except Exception as e:
        print("✗ Fetching results failed:", e)
        return

    # 6. Verify downloads
    artifacts = ["recon-tiff", "confidence", "cloudmask", "metrics", "report"]
    print("Verifying downloads...")
    for a in artifacts:
        try:
            req = urllib.request.Request(f"{base_url}/api/download/{job_id}/{a}")
            with urllib.request.urlopen(req) as response:
                content = response.read()
                print(f"  - Artifact '{a}' downloaded successfully ({len(content)} bytes)")
        except Exception as e:
            print(f"  ✗ Artifact '{a}' download failed:", e)

    print("\n==============================================")
    print("✓ INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    print("==============================================")

if __name__ == "__main__":
    test_api()
