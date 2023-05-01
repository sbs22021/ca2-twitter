# Mount disks in ubuntu
https://learn.microsoft.com/en-us/azure/virtual-machines/linux/attach-disk-portal?tabs=ubuntu

## Find the disk attached to the vm
```sh
lsblk -o NAME,HCTL,SIZE,MOUNTPOINT | grep -i "sd"
```

Output
```sh
sda     0:0:0:0      30G
├─sda1             29.9G /
├─sda14               4M
└─sda15             106M /boot/efi
sdb     1:0:1:0      14G
└─sdb1               14G /mnt
sdc     3:0:0:0       4G
```

## Format the disk

Replace `sdc` with the correct value for the attached disk

```sh
sudo parted /dev/sdc --script mklabel gpt mkpart xfspart xfs 0% 100%
sudo mkfs.xfs /dev/sdc1
sudo partprobe /dev/sdc1
```

## Mount disk
Create folder where to mount disk
```sh
sudo mkdir /usr/mongodata/db
```

Mount disk
```sh
sudo mount /dev/sdc1 /usr/mongodata/db
```

## Add to disk to /etc/fstab to persist after reboot

Find UUID of the disk `sudo blkid`

Edit file (example)
```sh
# CLOUD_IMG: This file was created/modified by the Cloud Image build process
UUID=1b1cdf6d-bd03-4f70-b3c3-d604b91cbb66       /        ext4   discard,errors=remount-ro       0 1
UUID=041F-28DD  /boot/efi       vfat    umask=0077      0 1
# UUID=bcc88de7-fbed-4b53-9f83-210bc99fb981   /usr/mongodbdata   xfs   defaults,nofail   1   2
UUID=a8ad67b9-aedf-4eb5-b3fa-0ec4d437149d       /usr/mongodbdata/db   xfs   defaults,nofail   1   2
UUID=ea615ac9-4a6c-4c3d-bec0-3068ed06cdfe       /usr/local/hadoop/hadoopdata/hdfs/datanode-01   xfs   defaults,nofail   1   2
/dev/disk/cloud/azure_resource-part1    /mnt    auto    defaults,nofail,x-systemd.requires=cloud-init.service,_netdev,comment=cloudconfig       0       2
```