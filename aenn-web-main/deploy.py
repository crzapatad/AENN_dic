import os
import argparse
from ftplib import FTP

def main():
  parser = argparse.ArgumentParser(description="Deploy script")
  parser.add_argument("--env", type=str, help="Environment to deploy", required=True)
  args = parser.parse_args()
  env = args.env

  FTP_SERVER = os.getenv("FTP_SERVER")
  FTP_USER = os.getenv("FTP_USER")
  FTP_PWD = os.getenv("FTP_PWD")

  with FTP(FTP_SERVER) as ftp:
    ftp.login(user=FTP_USER, passwd=FTP_PWD)
    if (env == "dev"): ftp.cwd("test")
    ftp_cleaner(ftp)
    
    path = os.path.dirname(os.path.realpath(__file__))
    ftp_uploader(ftp, path)

    ftp.quit()


def ftp_cleaner(ftp):
  # Cleaning assets folder from previous build
  print("[ i ] cleaning assets folder from previous build")
  to_delete_assets_ext = ["js", "css", "png", "svg", "jpg", "jpeg", "webp"]
  ftp.cwd("assets")
  for ext in to_delete_assets_ext:
    for file in ftp.nlst():
      if file.endswith(ext):
        ftp.delete(file)
        print("[ ok ] deleted asset " + file)
  
  ftp.cwd("..")

  # Cleaning root folder from previous build
  print("[ i ] cleaning root folder from previous build")
  to_delete_root_ext = ["html", "svg", "png", "jpg", "webp", "ico", "webmanifest", "xml"]
  for ext in to_delete_root_ext:
    for file in ftp.nlst():
      if file.endswith(ext):
        ftp.delete(file)
        print("[ ok ] deleted root " + file)


def ftp_uploader(ftp, path):
  print("[ i ] uploading files function initialized")

  dont_upload = ["deploy.py"]

  for filename in os.listdir(path):
    local_path = os.path.join(path, filename)

    if os.path.isfile(local_path):
      with open(local_path, "rb") as file:
        if filename in dont_upload: continue

        ftp.storbinary(f"STOR {filename}", file)
        print("[ ok ] uploaded file " + filename)

    elif os.path.isdir(local_path):
      if filename not in ftp.nlst():
        ftp.mkd(filename)
        print("[ ok ] created directory " + filename)
      ftp.cwd(filename)
      ftp_uploader(ftp, local_path)
      ftp.cwd("..")

if __name__ == "__main__":
  main()
