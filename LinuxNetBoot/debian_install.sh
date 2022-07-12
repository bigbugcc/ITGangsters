#!/usr/bin/bash
#Debian 网络安装配置程序

#内核源,末尾需要/
initUrl='https://ufile.fcwys.cc/cmd/sh/'
#安装源,末尾需要/
#repoUrl='https://mirrors.aliyun.com/debian/dists/stable/main/installer-amd64/current/images/netboot/'
repoUrl='https://mirrors.tuna.tsinghua.edu.cn/debian/dists/stable/main/installer-amd64/current/images/netboot/'
#boot路径
bootPath='/boot/'

#获取操作系统类型
ostype=$(cat /etc/os-release | grep ID | awk -F '=' 'NR==2{print $2}')

#判断Boot分区是否存在
if [ ! "$(lsblk -l | grep /boot)" == "" ];then
    bootPath='/'
    #获取启动分区号
    partnum=$(lsblk -l | grep /boot | awk '{print $2}' | cut -d ':' -f 2)
else
    #获取启动分区号
    partnum=$(lsblk -l | grep / | awk '{print $2}' | cut -d ':' -f 2)
fi;

#判断磁盘模式(mbr或gpt)
if [ $(fdisk -l | grep dos | sed 's/[^a-zA-Z0-9]//g') != "" ]; then
    #mbr模式
	diskmode=$(fdisk -l | grep dos | sed 's/[^a-zA-Z0-9]//g')
	diskmode=${diskmode:$((${#diskmode} - 3))}
	echo 'Disk mode is mbr.'
	bootpart=msdos${partnum}
else
    #gpt模式
    diskmode=$(fdisk -l | grep gpt | sed 's/[^a-zA-Z0-9]//g')
	diskmode=${diskmode:$((${#diskmode} - 3))}
	echo 'Disk mode is gpt.'
	bootpart=gpt${partnum}
fi

#判断文件夹是否存在
if [ -d /boot/debianboot/ ]; then 
    rm -rf /boot/debianboot/ && mkdir /boot/debianboot
    wget -4 -P /boot/debianboot/ ${initUrl}memdisk
    wget -4 -P /boot/debianboot/ ${repoUrl}mini.iso
else
    mkdir /boot/debianboot
    wget -4 -P /boot/debianboot/ ${initUrl}memdisk
    wget -4 -P /boot/debianboot/ ${repoUrl}mini.iso
fi;

#更改启动菜单
cat >/etc/grub.d/40_custom<<EOF
#!/bin/sh
exec tail -n +3 \$0
# This file provides an easy way to add custom menu entries.  Simply type the
# menu entries you want to add after this comment.  Be careful not to change
# the 'exec tail' line above.
menuentry "Install Debian" {
    insmod video_bochs
    insmod video_cirrus
    insmod all_video
    insmod gzio
    insmod part_gpt
    insmod ext2
    insmod xfs
    insmod iso9660
	insmod memdisk
    set root=(hd0,${bootpart})
    linux16 ${bootPath}debianboot/memdisk iso raw
    initrd16 ${bootPath}debianboot/mini.iso
	boot
}
EOF

#判断系统类型并更新引导菜单
if [ ${ostype} == 'debian' ]; then
	echo '### OS is debian.'
    sed -i 's/GRUB_DEFAULT\=0/GRUB_DEFAULT\=saved/g' /etc/default/grub
	grub-set-default "Install Debian"
	update-grub	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'ubuntu' ]; then
	echo '### OS is ubuntu.'
  sed -i 's/GRUB_DEFAULT\=0/GRUB_DEFAULT\=saved/g' /etc/default/grub
	grub-set-default "Install Debian"
	update-grub	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'centos' ]; then
	echo '### OS is centos.'
	grub2-set-default "Install Debian"
	grub2-mkconfig -o /etc/grub2.cfg	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'rocky' ]; then
	echo '### OS is rocky.';
	grub2-set-default "Install Debian"
	grub2-mkconfig -o /etc/grub2.cfg	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'fedora' ]; then
	echo '### OS is fedora.'
	grub2-set-default "Install Debian"
	grub2-mkconfig -o /etc/grub2.cfg	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'rhel' ]; then
	echo '### OS is rhel.'
	grub2-set-default "Install Debian"
	grub2-mkconfig -o /etc/grub2.cfg	
	echo -e "\n### Config Success, Please Reboot System.\n"
else 
	echo '### OS is '${ostype}, no support.
fi

