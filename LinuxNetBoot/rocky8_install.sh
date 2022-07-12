#!/usr/bin/sh
#Rocky8 网络安装配置程序

#内核源,末尾需要/
initUrl='https://mirrors.nju.edu.cn/rocky/8/BaseOS/x86_64/os/'
#安装源,末尾需要/
repoUrl='https://mirrors.nju.edu.cn/rocky/8/BaseOS/x86_64/os/'
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

#更改启动菜单
cat >/etc/grub.d/40_custom<<EOF
#!/bin/sh
exec tail -n +3 \$0
# This file provides an easy way to add custom menu entries.  Simply type the
# menu entries you want to add after this comment.  Be careful not to change
# the 'exec tail' line above.
menuentry "Install Rocky 8" {
    insmod video_bochs
    insmod video_cirrus
    insmod all_video
    insmod gzio
    insmod part_gpt
    insmod ext2
    insmod xfs
    insmod iso9660
    set root=(hd0,${bootpart})
    linux16 ${bootPath}rockyboot/vmlinuz initrd=initrd.img inst.repo=${repoUrl}
    initrd16 ${bootPath}rockyboot/initrd.img
}
EOF

#判断系统类型并更新引导菜单
if [ ${ostype} == 'debian' ]; then
	echo '### OS is debian.'
    sed -i 's/GRUB_DEFAULT\=0/GRUB_DEFAULT\=saved/g' /etc/default/grub
	grub-set-default "Install Rocky 8"
	update-grub	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'ubuntu' ]; then
	echo '### OS is ubuntu.'
  sed -i 's/GRUB_DEFAULT\=0/GRUB_DEFAULT\=saved/g' /etc/default/grub
	grub-set-default "Install Rocky 8"
	update-grub	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'centos' ]; then
	echo '### OS is centos.'
	grub2-set-default "Install Rocky 8"
	grub2-mkconfig -o /etc/grub2.cfg	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'rocky' ]; then
	echo '### OS is rocky.';
	grub2-set-default "Install Rocky 8"
	grub2-mkconfig -o /etc/grub2.cfg	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'fedora' ]; then
	echo '### OS is fedora.'
	grub2-set-default "Install Rocky 8"
	grub2-mkconfig -o /etc/grub2.cfg	
	echo -e "\n### Config Success, Please Reboot System.\n"
elif [ ${ostype} == 'rhel' ]; then
	echo '### OS is rhel.'
	grub2-set-default "Install Rocky 8"
	grub2-mkconfig -o /etc/grub2.cfg	
	echo -e "\n### Config Success, Please Reboot System.\n"
else 
	echo '### OS is '${ostype}, no support.
fi


