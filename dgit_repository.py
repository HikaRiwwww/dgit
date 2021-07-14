import os
import configparser


class DgitRepository:
    """
    类似于GitRepository
    """

    def __init__(self, path, force=False):
        """
        返回一个仓库实例
        :param path: 需要被版本控制的项目所在路径
        :param force: 如果为True则忽略文件路径合法性校验并创建一个新的.git目录
        """
        self.worktree = path
        self.dgit_dir = os.path.join(path, ".git")

        # 路径不合法且不强制创建.git目录则抛出异常
        if not (force or os.path.isdir(self.dgit_dir)):
            raise Exception("Not an legal path: {}".format(self.dgit_dir))

        self.conf = configparser.ConfigParser()

        # 获取配置conf文件路径
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Missing configuration file!")

        if not force:
            ver_num = int(self.conf.get("core", "repositoryformatversion"))
            if ver_num != 0:
                raise Exception("Unsupported repositoryformatversion: {}".format(ver_num))


def repo_path(repo: DgitRepository, *path):
    """
    拼接仓库配置文件的路径
    :param repo:
    :param path:
    :return:
    """
    return os.path.join(repo.dgit_dir, *path)


def repo_dir(repo, *path, mkdir=False):
    """
    判断文件夹路径是否存在
        如果存在且为文件夹则返回，不是文件夹则抛出异常
        如果不存在且不创建，返回None，否则创建路径并返回
    :param repo:
    :param path:
    :param mkdir:
    :return:
    """
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            raise Exception("Not a directory: {}".format(path))

    else:
        if mkdir:
            os.makedirs(path)
            return path
        return None


def repo_file(repo, *path, mkdir=False):
    """
    能拿到路径就返回路径，拿不到就返回None
    :param repo:
    :param path:
    :param mkdir:
    :return:
    """
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)


def default_repo_conf():
    c = configparser.ConfigParser()
    c.add_section("core")
    c.set("core", "repositoryformatversion", "0")
    c.set("core", "filemode", "false")
    c.set("core", "bare", "false")
    return c


def repo_create(path):
    """
    新建一个仓库
    :param path:
    :return:
    """
    repo = DgitRepository(path, True)

    # 检查工作树目录，不是文件夹或者文件夹非空都抛异常，如果不存在该目录则新建
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception("Not a directory: {}".format(repo.worktree))
        if os.listdir(repo.worktree):
            raise Exception("Not an empty directory: {}".format(repo.worktree))
    else:
        os.makedirs(repo.worktree)

    # 创建各个子目录
    assert (repo_dir(repo, "branches", mkdir=True))
    assert (repo_dir(repo, "objects", mkdir=True))
    assert (repo_dir(repo, "refs", "tags", mkdir=True))
    assert (repo_dir(repo, "refs", "heads", mkdir=True))

    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    with open(repo_file(repo, "config"), "w") as f:
        config = default_repo_conf()
        config.write(f)

    return repo


def repo_find(path=".", required=True):
    """
    todo:
        2021-07-13：没理解这个有什么用，如果仓库已经初始化了还调用这个命令干嘛，预防性编码？
    向上递归寻找git仓库，如果获取到了则在那里初始化仓库，否则抛出异常或返回None
    :param path:
    :param required:
    :return:
    """
    path = os.path.abspath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return DgitRepository(path)

    parent = os.path.relpath(os.path.join(path, ".."))

    # 如果已经递归至根目录
    if parent == path:
        if required:
            raise Exception("Dgit repository not found")
        else:
            return None

    return repo_find(parent, required)
