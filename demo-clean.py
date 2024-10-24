import os
import sys

def main():
    files_to_delete = [
        "owner_lee/root.layout",
        "developer_kang/clone.210dcc50.link",
        "developer_kang/update-version.210dcc50.link",
        "developer_kang/demo-project",
        "developer_kim/package.be06db20.link",
        "developer_kim/demo-project.tar.gz",
        "developer_kim/demo-project",
        "developer_kim/sbom.json",
        "developer_kim/generate-sbom.be06db20.link",
        "final_product/lee.pub",
        "final_product/demo-project.tar.gz",
        "final_product/package.be06db20.link",
        "final_product/clone.210dcc50.link",
        "final_product/update-version.210dcc50.link",
        "final_product/untar.link",
        "final_product/root.layout",
        "final_product/demo-project",
        "final_product/sbom.json",
        "final_product/generate-sbom.be06db20.link",
    ]

    for path in files_to_delete:
      if os.path.isfile(path):
        os.remove(path)
      elif os.path.isdir(path):
        rmtree(path)

    sys.exit(0)    

if __name__ == '__main__':
  main()