FROM alpine:3.10.3
LABEL maintainer="mpodroid@gmail.com"

RUN apk add --no-cache qpdf

RUN mkdir /pdf

WORKDIR /pdf
