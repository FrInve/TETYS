# Use an official Node.js image as the base
FROM node:18 AS build

# Set the working directory inside the container
WORKDIR /usr/src/app/

# Copy package.json and package-lock.json
COPY ./tetysDashboard/package*.json ./

RUN npm install -g @angular/cli

# Install project dependencies
RUN npm install 

# Copy the rest of the application code to the working directory
COPY ./tetysDashboard /usr/src/app

# Build the Angular app with the correct base href for production
RUN npm run build -- --base-href=/tetys/


# Expose port 4200 to access the Angular dev server from outside the container
EXPOSE 4200

# Start the Angular app in development mode (with live reload)
CMD ["npm", "run", "start"]

