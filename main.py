from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, UseCurrentSession
import asyncio
import os

async def logoutThisSession(client: type[TelegramClient]):
    # Logout this session
    result = await client.log_out()
    
    if result:
        print("Logged out successfully")
        return True
    else:
        print("Failed to log out")
        return False
        
async def generateNewTData(profileName: str, client: type[TelegramClient], password: str = None):
    # verify directory - if it exists, delete all files and folders inside
    # if directory doesn't exist, create it
    output_dir = f"output/{profileName}"
    if os.path.exists(output_dir):
        # Delete all files and folders inside the directory
        for root, dirs, files in os.walk(output_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    # create new API device
    api = API.TelegramDesktop.Generate(system="windows", unique_id=f"{profileName}.session")
    newClient = await client.QRLoginToNewClient(session=f"{output_dir}/{profileName}.session", api=api, password=password)
    
    if not isinstance(newClient, TelegramClient):
        print("Error: newClient is not of type TelegramClient")
        return False
    
    await newClient.connect()
    
    newTDesktop = await newClient.ToTDesktop()
    # Save the new tdata folder
    newTDesktop.SaveTData(fr"{output_dir}/tdata")

    print("New tdata folder generated successfully")
    return True

def getListProfiles(pathToFolder: str):
    # Get all folders in the path
    folders = [f for f in os.listdir(pathToFolder) if os.path.isdir(os.path.join(pathToFolder, f))]
    
    # Filter out folders that don't contain tdata
    tDataFolders = []
    for folder in folders:
        tDataPath = os.path.join(pathToFolder, folder, "tdata")
        if os.path.exists(tDataPath):
            tDataFolders.append(folder)
    return tDataFolders
    

async def main():
    print("Hãy nhập chế độ muốn sử dụng")
    print("1: Tạo tdata mới")
    print("2: Đăng xuất phiên đăng nhập từ tdata hiện tại")
    
    mode = input("Nhập chế độ muốn chạy (1 hoặc 2): ").strip()
    if mode not in ["1", "2"]:
        print("Chế độ không hợp lệ. Vui lòng chạy lại chương trình.")
        return
    
    profiles = getListProfiles("input")
    if not profiles:
        print("Không tìm thấy tdata nào trong thư mục đầu vào.")
        return
    
    for profile in profiles:
        print(f"Đang xử lý profile: {profile}")
        tDataFolder = fr"input/{profile}/tdata"
        tDesk = TDesktop(tDataFolder)
        
        if not tDesk.isLoaded():
            print(f"Không thể tải tdata cho profile: {profile}")
            continue
        
        client = await tDesk.ToTelethon(session=f"input/{profile}/{profile}.session", flag=UseCurrentSession)
        
        #check client is valid auth
        try:
            await client.GetSessions()
        except Exception as e:
            print(f"Lỗi không sử dụng được tdata của profile {profile}: {e}")
            continue
        
        if mode == "1":
            await generateNewTData(profileName=profile, client=client)
        elif mode == "2":
            await logoutThisSession(client)
            
asyncio.run(main())