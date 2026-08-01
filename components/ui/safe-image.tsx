"use client"

import Image, { type ImageProps } from "next/image"
import { ImageOff } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"

type SafeImageProps = Omit<ImageProps, "src"> & {
  src?: string | null
  fallbackSrc?: string
  wrapperClassName?: string
}

export function SafeImage({
  src,
  fallbackSrc = "/images/liss-iv-cloudy.png",
  alt,
  className,
  wrapperClassName,
  ...props
}: SafeImageProps) {
  const desiredSrc = src || fallbackSrc
  const [errorState, setErrorState] = useState({
    src: desiredSrc,
    primaryFailed: false,
    fallbackFailed: false,
  })

  const primaryFailed = errorState.src === desiredSrc && errorState.primaryFailed
  const fallbackFailed = errorState.src === desiredSrc && errorState.fallbackFailed
  const currentSrc = primaryFailed ? fallbackSrc : desiredSrc

  if (fallbackFailed) {
    return (
      <div
        className={cn(
          "absolute inset-0 flex items-center justify-center bg-secondary text-muted-foreground",
          wrapperClassName,
        )}
        role="img"
        aria-label={alt}
      >
        <ImageOff className="size-7" aria-hidden="true" />
      </div>
    )
  }

  return (
    <Image
      {...props}
      src={currentSrc}
      alt={alt}
      className={className}
      onError={() => {
        if (!primaryFailed) {
          setErrorState({ src: desiredSrc, primaryFailed: true, fallbackFailed: false })
          return
        }
        setErrorState({ src: desiredSrc, primaryFailed: true, fallbackFailed: true })
      }}
    />
  )
}
