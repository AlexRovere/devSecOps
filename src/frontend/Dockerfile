FROM nginx:alpine3.21@sha256:c3f8e73fdb79deaebaa2037150150191b9dcbfba68b4a46d70103204c53f4709
LABEL maintainer="Al Rov"
LABEL description="Image for nginx front of Task Manager application"
LABEL version=1.0

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY . /usr/share/nginx/html
