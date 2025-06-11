# Use official Ruby image as base
FROM ruby:3.1-slim

# Install essential dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /site

# Copy Gemfile and Gemfile.lock
COPY Gemfile Gemfile.lock ./

# Install bundler and dependencies
RUN gem install bundler:2.3.12 && \
    bundle config set --local deployment 'true' && \
    bundle install

# Copy the rest of the site
COPY . .

# Build the Jekyll site
RUN JEKYLL_ENV=production bundle exec jekyll build

# Use nginx to serve the static files
FROM nginx:alpine

# Copy the built site from the builder stage
COPY --from=0 /site/_site /usr/share/nginx/html

# Copy custom nginx config if needed
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ $uri.html =404; \
    } \
    error_page 404 /404.html; \
}' > /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]