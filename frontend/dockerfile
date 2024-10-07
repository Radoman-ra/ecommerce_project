FROM node:20.17.0

WORKDIR /app

COPY . .

RUN rm -rf package-lock.json node_modules && npm install

EXPOSE 5173

CMD ["npm", "run", "dev"]
