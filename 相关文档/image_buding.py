import docker
from config.config import docker_url,harbor_url,harbor_usr,harbor_pwd,harbor_base_tag,repository
from core.harbor_api import HarborapiV2

def buding(new_tag,file_name,file_dir,user_lab,old_tag):
    msg_base = {"status":"error","msg":""}
    # 建立docker的tcp连接
    try:
        client = docker.DockerClient(base_url=docker_url)
    except Exception as err:
        print(err)
        msg_base["msg"] = "远程端docker连接异常"
        return msg_base
    # 根据dockerfile构建镜像,这里tag直接打好到仓库目录下k8s-test-3.novalocal:9330/test/
    try:
        client.images.build(path=file_dir,dockerfile=file_name,tag=new_tag)
    except Exception as err:
        err_msg = str(err)
        if "git" in err_msg:
            print(err_msg)
            msg_base["msg"] = "所传入的dockerfile无git"
            return msg_base
        msg_base["msg"] = err_msg
        return msg_base
    # 运行容器
    container = client.containers.run(image=new_tag,detach=True)
    # 获取容器id
    print(container.id)
    # 停止容器
    container.stop()
    # 连接harbor
    try:
        client.login(registry=harbor_url,username=harbor_usr,password=harbor_pwd)
    except Exception as err:
        print(err)
        msg_base["msg"] = "harbor登入失败"
        return msg_base
    # 上传镜像
    msg = client.images.push(repository=new_tag)
    client.close()
    if "ERROR" in msg.upper():
        msg_base["msg"] = "镜像上传异常"
        return msg_base
    else:
        pro_info = HarborapiV2(harbor_base_tag, harbor_usr, harbor_pwd)
        repo_new = repository.replace("/","")
        pro_info.fetch_pros_id(repo_new)
        flag = pro_info.create_labes(user_lab)
        if not isinstance(flag,bool):
            return flag
        lab_id = pro_info.fetch_label_id(user_lab)
        tag_list = old_tag.split(":")
        image_name = tag_list[0]
        tag = tag_list[1]
        val = pro_info.binding_lab(repository, image_name, tag, lab_id)
        if not isinstance(val,bool):
            return val
        msg_base["status"] = "success"
        msg_base["msg"] = "镜像上传成功"
        return msg_base

