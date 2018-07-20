
#It will remove all the previous docker engine
docker -v
if [ echo "$?" = "127" ]
then
sudo apt-get remove docker docker-engine docker.io
sudo apt-get update
# Now install docker repo
sudo apt-get install     apt-transport-https     ca-certificates     curl     software-properties-common
 2023  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
  
# install docker-ce 
sudo apt-get update
sudo apt-get install docker-ce

else
    echo "yesss exist"
fi

# after getting the docker-ce
if [ -z "$(docker images -q redislabs/redisgraph:latest)" ]
then
    echo "yes exist"

else 
    git clone https://github.com/swilly22/redis-graph.git
    cd redis-graph
    sudo make docker
fi
# command for run the server 
sudo docker run -p 6379:6379 redislabs/redisgraph
