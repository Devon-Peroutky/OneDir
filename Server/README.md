This is where the Server Prototypes can go. Create a directory for the technology (ex. 'Twisted') and put all the necessary code in there.


##### server_conf.sh
* creates a testing server for ftplib
* needs root access
* create server: **sudo bash server_conf.sh make**
* delete server: **sudo bash server_conf.sh delete**
* files will be created two directories back:
  * ../../tesing_server (folder)
    * server.py (file)
    * server_map.txt (file)
    * User.db (file)
    * sql (folder)
      * _ _ init _ _.py (file)
      * sql_manager.py (file)
    * user2 (folder)
      * shared_folder (folder) 
        * shared_file.txt (file)
    * user1 (folder)
      * download_from (folder)
        * to_download.txt (file)
      * upload_to (folder)
        * (empty)
      * shared_folder (folder) 
        * NOTE: the file in this folder was not created, it was mounted into this folder
        * shared_file.txt (file) 
* Any changes in shared_folder will happen in both places, not just one
* Run sever with: **sudo bash start_server.sh**
