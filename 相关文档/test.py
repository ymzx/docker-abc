import docker
# 建立docker的tcp连接
client = docker.DockerClient(base_url="tcp://10.0.103.46:2375")
# 根据dockerfile构建镜像,这里tag直接打好到仓库目录下k8s-test-3.novalocal:9330/test/
images = client.images.build(path='./',dockerfile="Dockerfile",tag="k8s-test-3.novalocal:9330/test/test:v1")
# 运行容器
container = client.containers.run(image="k8s-test-3.novalocal:9330/test/test:v1",ports={"33060":"33060"},detach=True)
# 查看容器id
print(container.id)
# 停止容器
# container.stop()

# 连接harbor
client.login(registry="http://k8s-test-3.novalocal:9330",username="admin",password="Harbor12345")
# 上传镜像
s = client.images.push(repository='k8s-test-3.novalocal:9330/test/test:v1')
if 'ERROR' in s.upper():
    print(s)