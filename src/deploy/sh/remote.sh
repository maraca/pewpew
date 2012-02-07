s3cmd get s3://$1/$2 /app/ &&
cd /app/ &&
tar -xf $2 &&
ln -sfn $3 latest &&
cd latest && bin/buildout -o 
