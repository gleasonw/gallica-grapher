echo "Deploying Frontend..."

npm run build

aws s3 sync build/ s3://gallica-ngram-grapher