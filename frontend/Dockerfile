#The plan: create Docker file to push to AWS s3, follow
# tutorial on using cloudfront to route requests ot backend,
# figuring out how to connect the DB from there.

FROM node:alpine as builder

WORKDIR /app/frontend

COPY package.json package.json

RUN npm install

COPY . .

RUN npm run build

FROM mesosphere/aws-cli

COPY --from=builder /app/frontend/build .

CMD ["s3", "sync", "./", "s3://gallica-ngram-grapher"]