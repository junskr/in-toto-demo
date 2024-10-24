from cryptography.hazmat.primitives.serialization import load_pem_private_key
from securesystemslib.signer import CryptoSigner
from in_toto.models._signer import load_public_key_from_file
from in_toto.models.layout import Layout
from in_toto.models.metadata import Envelope

"""
# import 하는 모듈/클래스/함수의 설명입니다.
from cryptography.hazmat.primitives.serialization import load_pem_private_key
 - 개인키를 로드하는 데 사용됩니다. 개인키는 레이아웃을 서명할 때 필요합니다.
from securesystemslib.signer import CryptoSigner
 - 개인키로 데이터를 서명하기 위한 객체를 생성합니다.
from in_toto.models._signer import load_public_key_from_file
 - 공개키를 파일에서 로드합니다. 공개키는 서명 검증에 사용됩니다.
from in_toto.models.layout import Layout
 - 레이아웃을 정의하는 객체입니다. 레이아웃은 소프트웨어 공급망에서 수행되는 단계들을 나타냅니다.
from in_toto.models.metadata import Envelope
 - 레이아웃을 서명하고 저장할 때 필요한 메타데이터 형식을 나타냅니다.
"""

def main():
  # Lee 라는 이름의 파일에서 PEM형식의 개인키 lee를 읽습니다.
  # 개인키는 소프트웨어 배포 과정에서 데이터를 서명하고 그 무결성을 보장하는 데 사용됩니다.
  with open("lee", "rb") as f:
    key_lee = load_pem_private_key(f.read(), None)

  # lee의 개인키를 사용해 서명을 생성할 수 있는 CryptoSigner 객체를 만듭니다. 이 객체는 레이아웃을 서명하는 데 사용됩니다.
  signer_lee = CryptoSigner(key_lee)
  # kang과 kim의 공개키를 파일에서 로드합니다.
  # 이 공개키들은 그들이 소프트웨어 개발의 특정 단계에서 작업할 수 있는 권한이 있음을 나타냅니다.
  key_kang  = load_public_key_from_file("../developer_kang/kang.pub")
  key_kim  = load_public_key_from_file("../developer_kim/kim.pub")  

  # 레이아웃을 정의합니다.
  layout = Layout.read({
      "_type": "layout",
      # kang과 kim의 공개키가 레이아웃에 포함됩니다.
      # 그들이 작업을 수행할 수 있는 권한이 있음을 의미합니다.
      "keys": {
          key_kang["keyid"]: key_kang,
          key_kim["keyid"]: key_kim,
      },
      # steps: 레이아웃에서 소프트웨어 공급망의 각 단계를 정의합니다.
      # 첫 번째 단계의 이름은 clone 입니다. 이 단계에서는 git clone 명령을 사용하여 프로젝트를 복제합니다.
      "steps": [{
          "name": "clone",
          # expected_materials: 작업(clone)을 수행하기 전 필요로 하는 파일(입력 파일)
          # 입력 파일은 아무것도 없습니다.
          "expected_materials": [],
          # expected_products : 작업(clone)을 수행한 후 생성되는 파일(결과 파일)
          # in-toto-demo-project/foo.py 파일이 생성되며, 그 외 파일은 생성되지 않아야합니다. 모두 DISALLOW
          "expected_products": [["CREATE", "in-toto-demo-project/foo.py"], ["DISALLOW", "*"]],
          # 이 단계는 kong의 개인키를 가진 사람만 수행할 수 있습니다. kang의 개인키로 서명합니다.
          "pubkeys": [key_kang["keyid"]],
          # expected_command: 작업(clone)을 수행할 때, 실행될 명령어입니다.
          # git clone https://github.com/junskr/in-toto-demo-project.git
          "expected_command": [
              "git",
              "clone",
              "https://github.com/junskr/in-toto-demo-project.git"
          ],
          # 최소 1명의 작업자가 이 작업을 성공적으로 완료하여야 합니다.
          # 지금은 kang의 개인키만 허용하였지만, 허용된 개인키가 다수일 경우 의미가 있는 숫자입니다.
          "threshold": 1,
        },{
          # 두 번째 단계의 이름은 update-version 입니다. 이 단계에서는 파일의 버전을 수정합니다.
          "name": "update-version",
          # 이 단계는 이전 단계(clone)에서 생성된 파일(in-toto-demo-project/*)이 필요합니다.
          "expected_materials": [["MATCH", "in-toto-demo-project/*", "WITH", "PRODUCTS",
                                "FROM", "clone"], ["DISALLOW", "*"]],
          # 이 단계는 foo.py이 수정되어야 하며, 그 외 다른 파일들은 수정되지 않아야 합니다. 모두 DISALLOW
          "expected_products": [["MODIFY", "in-toto-demo-project/foo.py"], ["DISALLOW", "*"]],
          # 이 단계는 kong의 개인키를 가진 사람만 수행할 수 있습니다. kang의 개인키로 서명합니다.
          "pubkeys": [key_kang["keyid"]],
          # 이 단계에서 실행될 명령은 지정되지 않았습니다.
          "expected_command": [],
          # 최소 1명의 작업자가 이 작업을 성공적으로 완료하여야 합니다.
          # 지금은 kang의 개인키만 허용하였지만, 허용된 개인키가 다수일 경우 의미가 있는 숫자입니다.          
          "threshold": 1,
        },{
          # 세 번째 단계의 이름은 package 입니다. 이 단계에서는 프로젝트 파일을 tar.gz으로 압축합니다.
          "name": "package",
          # 이 단계에서는 이전 단계(update-version) 단계에서 수정된 파일이 필요합니다.
          "expected_materials": [
            ["MATCH", "in-toto-demo-project/*", "WITH", "PRODUCTS", "FROM",
             "update-version"], ["DISALLOW", "*"],
          ],
          # 이 단계에서는 결과물로 in-toto-demo-project.tar.gz 파일이 생성됩니다. 그 외엔 모두 DISALLOW
          "expected_products": [
              ["CREATE", "in-toto-demo-project.tar.gz"], ["DISALLOW", "*"],
          ],
          # 이 단계는 kim의 개인키를 가진 사람만 수행할 수 있습니다. kim의 개인키로 서명합니다.
          "pubkeys": [key_kim["keyid"]],
          # 이 단계에서는 tar 명령을 실행하여 압축 파일을 생성합니다.
          "expected_command": [
              "tar",
              "--exclude",
              ".git",
              "-zcvf",
              "in-toto-demo-project.tar.gz",
              "in-toto-demo-project",
          ],
          # 최소 1명의 작업자가 이 작업을 성공적으로 완료하여야 합니다.
          # 지금은 kang의 개인키만 허용하였지만, 허용된 개인키가 다수일 경우 의미가 있는 숫자입니다.               
          "threshold": 1,
        },{
          # 네 번째 단계의 이름은 generate-sbom 입니다. 이 단계에서는 SBOM을 서명합니다.
          "name": "generate-sbom",
          # 이 단계에서는 (update-version)단계에서 수정된 파일과 (package)단계에서 압축된 파일이 필요합니다. 그 외엔 모두 DISALLOW
          "expected_materials": [
            ["MATCH", "demo-project/*", "WITH", "PRODUCTS", "FROM",
             "update-version"], 
            ["MATCH", "demo-project.tar.gz", "WITH", "PRODUCTS", "FROM",
             "package"], 
            ["DISALLOW", "*"]
          ],
          # 이 단계에서는 결과물로 sbom.json 파일이 생성됩니다. 그 외엔 모두 DISALLOW
          "expected_products": [
              ["CREATE", "sbom.json"], ["DISALLOW", "*"],
          ],
          # 이 단계는 kim의 개인키를 가진 사람만 수행할 수 있습니다. kim의 개인키로 서명합니다.
          "pubkeys": [key_carl["keyid"]],
          # 이 단계에서 실행될 명령은 지정되지 않았습니다.
          # 즉, SBOM 생성 도구는 자유롭게 선택 및 사용 가능합니다.
          "expected_command": [],
          # 최소 1명의 작업자가 이 작업을 성공적으로 완료하여야 합니다.
          # 지금은 kang의 개인키만 허용하였지만, 허용된 개인키가 다수일 경우 의미가 있는 숫자입니다.             
          "threshold": 1,
        }],
      # inspect: 검사를 수행 내용을 정의합니다.
      "inspect": [{
          # 검사의 이름은 untar 입니다. 파일을 압축 해제하는 검사를 수행합니다.
          "name": "untar",
          # 이 단계에서는 package 단계에서 생성된 demo-project.tar.gz 파일과
          # generate-sbom 단계에서 생성된 sbom.json이 필요합니다.
          # 기본적으로 가지고 있던 .keep 파일과 owner로 부터 받은 lee.pub, root.layout 그리고 link 파일들만 허용합니다. 그 외엔 모두 DISALLOW
          "expected_materials": [
              ["MATCH", "in-toto-demo-project.tar.gz", "WITH", "PRODUCTS", "FROM", "package"],
              ["MATCH", "sbom.json", "WITH", "PRODUCTS", "FROM", "generate-sbom"],
              ["ALLOW", ".keep"],
              ["ALLOW", "lee.pub"],
              ["ALLOW", "root.layout"],
              ["ALLOW", "*.link"],
              ["DISALLOW", "*"]
          ],
          # 압축이 해제된 후에는 foo.py 파일과 기타 허용(ALLOW)된 파일만 존재해야 합니다.
          # 압축이 해제되면, update-version 단계에서 수정된 foo.py 파일과 git 관련 파일, tar.gz 압축파일, 
          # generate-sbom 단계에서 생성된 sbom.json 파일
          # 그리고 기본적으로 가지고 있던 .keep 파일과 owner로 부터 받은 lee.pub, root.layout 그리고 link 파일들만 있어야합니다. 그 외엔 모두 DISALLOW
          "expected_products": [
              ["MATCH", "in-toto-demo-project/foo.py", "WITH", "PRODUCTS", "FROM", "update-version"],
              ["ALLOW", "in-toto-demo-project/.git/*"],
              ["ALLOW", "in-toto-demo-project.tar.gz"],
              ["ALLOW", "sbom.json"],
              ["ALLOW", ".keep"],
              ["ALLOW", "lee.pub"],
              ["ALLOW", "root.layout"],
              ["ALLOW", "*.link"],
              ["DISALLOW", "*"]
          ],
          # 이 단계에서는 tar xzf 명령을 사용해 파일을 압축 해제합니다.
          "run": [
              "tar",
              "xzf",
              "in-toto-demo-project.tar.gz",
          ]
        }],
  })

  # 레이아웃을 서명 가능한 메타데이터 형식으로 변환합니다.
  metadata = Envelope.from_signable(layout)

  # lee의 개인키로 레이아웃을 서명합니다.
  metadata.create_signature(signer_lee)
  # 레이아웃을 root.layout 파일에 저장합니다.
  metadata.dump("root.layout")

  print('Created demo in-toto layout as "root.layout".')

if __name__ == '__main__':
  main()
