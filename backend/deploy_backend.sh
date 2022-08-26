echo "Deploying Backend..."
aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin 254923847141.dkr.ecr.us-west-1.amazonaws.com/gallica-grapher-backend
docker build -t gallica-grapher-backend .
docker tag gallica-grapher-backend:latest 254923847141.dkr.ecr.us-west-1.amazonaws.com/gallica-grapher-backend:latest
docker push 254923847141.dkr.ecr.us-west-1.amazonaws.com/gallica-grapher-backend:latest
cd aws_deploy
eb deploy