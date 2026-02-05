FROM nginx:stable-alpine3.21@sha256:30f1c0d78e0ad60901648be663a710bdadf19e4c10ac6782c235200619158284
LABEL maintainer="Al Rov"
LABEL description="Image for nginx front of Task Manager application"
LABEL version=1.0

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY . /usr/share/nginx/html
