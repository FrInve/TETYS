FROM node:22-alpine as builder
WORKDIR /app
COPY tetysDashboard/package*.json ./
RUN npm install
COPY ./tetysDashboard .
RUN npm run build -- --base-href=/tetys/ #-- --configuration production

FROM nginx:latest
EXPOSE 80
COPY --from=builder /app/dist/tetys-dashboard/browser /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
