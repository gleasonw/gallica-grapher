echo "Deploying Frontend..."

npm run build

aws s3 sync build/ s3://gallica-ngram-grapher

aws cloudfront create-invalidation --distribution-id E1MKOLBVZNJ89G --paths "/*"