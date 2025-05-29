# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all files
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration template
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Expose port
EXPOSE 80

# The nginx:alpine image automatically runs envsubst on *.template files in /etc/nginx/templates/
# and outputs the result to /etc/nginx/conf.d/ when the container starts
CMD ["nginx", "-g", "daemon off;"]
