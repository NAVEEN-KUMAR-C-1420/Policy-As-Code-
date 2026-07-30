FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Expose Vite's default dev port
EXPOSE 5173

# Run the dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
