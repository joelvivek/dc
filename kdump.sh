#!/bin/bash
##Copyright (c) 2016, 2016-2017  by RJIL.
## All Rights Reserved
## THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE.
## The copyright notice above does not evidence any actual or
## intended publication of such source code.
##***********************************************************
## Filename : Change_Configuration_RHEL.sh
##***********************************************************
## Authors  : Vivek Singh(vivek9.singh@ril.com)
## Usage    :sh Change_Configuration_RHEL.sh
## Debug    :sh -x Change_Configuration_RHEL.sh
## OS       :RHEL5.x/6.x Centos 5.x/6.x/6
##The script make changes in the configuration file and is supported on the OS listed above only.
##Services/Deamons Affected:Iptables,kdump,avahi-deamon
##Configuration Files Changed:/etc/ntpd,/etc/sysconfig/ntpdate,/etc/sysconfig/ntpd./etc/syslog.conf,/etc/rsyslog.conf contd...
##/etc/sysctl.conf,/etc/kdump.conf,/boot/grub/grub.conf...
##LOG FILE:Please check the logs in the file var/log/SAconfig/Config_RHEL.log

############Variable Declaration##############################################
LOG_DIR="/var/log/SAconfig"
LOGFILE="/var/log/SAconfig/Config_RHEL.log"
Rsyslog_File="/etc/rsyslog.conf"
NTPD_FILE="/etc/sysconfig/ntpd"
NTPDATE_FILE="/etc/sysconfig/ntpdate"
NTPDATE_FILE_RHEL5="/etc/sysconfig/ntpd"
PATTERN_RSYSLOG="REMSTLOG.CLMS.JIO.COM:514"
PATTERN_NTPD="ntp:ntp -p /var/run/ntpd.pid"
PATTERN_NTPDATE="SYNC_HWCLOCK=yes"
#Rsyslog_cmd='echo "*.*     @REMSTLOG.CLMS.JIO.COM:514" | tee -a /etc/rsyslog.conf'
NTPD_CMD='grep -q "^OPTIONS=" /etc/sysconfig/ntpd && sed -i 's#^OPTIONS=.*#OPTIONS="-x -u ntp:ntp -p /var/run/ntpd.pid -g"#' /etc/sysconfig/ntpd || sed -i /etc/sysconfig/ntpd 'a#OPTIONS="-x -u ntp:ntp -p /var/run/ntpd.pid -g"''
if grep -q -i "release 6" /etc/redhat-release
then
NTPDATE_CMD='sed -i.bak 's/SYNC_HWCLOCK=no/SYNC_HWCLOCK=yes/g' /etc/sysconfig/ntpdate'
else
NTPDATE_CMD_RHEL5='sed -i.bak 's/SYNC_HWCLOCK=no/SYNC_HWCLOCK=yes/g' /etc/sysconfig/ntpd'
fi
CHECKSIZE="/tmp/size.txt"

#############Function Declaration############################################
function Success() {
local msg2=$1
local msg3=$2
echo -e "$(date +%F\ %H:%M:%S) $LOGNAME $1 $2" >> "$LOGFILE"
}
function Error() {
local msg2=$1
local msg3=$2
echo -e "$(date +%F\ %H:%M:%S) $LOGNAME $1 $2" >> "$LOGFILE"
}

function Check_Pattern() {
pattern=$1
filename=$2
grep "$pattern" $filename > $CHECKSIZE
if [ -s $CHECKSIZE ];then
   echo "Success:The File "$filename" has been changed Succesfully"
   Success "Success:" "The File "$filename" has been changed Succesfully"
   else
   echo "Failure:The File "$filename" has not been changed"
 fi
}

function Check_User () {
USERNAME=$1
STATUS="false"
getent passwd $USERNAME >/dev/null 2>&1 && STATUS=true
if [ "$STATUS" == "true" ];then
Success "INFO:" "User "$USERNAME" is already present on the server"
else
for user in $USERNAME
do
Create_User $user
done
fi 
}  
function Create_User() {
USERNAME=$1

    echo "Creating User $USERNAME on Server"
	if [ "$USERNAME" == "idcadm" ];then
	useradd -m -o -u 5000 -d /home/idcadm -p '$6$ZaLlfQO3$c7wolsNA8UcvgJBxIQ2u4W3gArZiGrB0two55FlWDbFNLdJZNYqfbQu2694WNr7rvWacU1Enxtl/idr4NPgIw1' idcadm
	if [ $? -eq 0 ];then
	echo "SUCCESS:User "$USERNAME" added Successfully on server"
	Success "Success:" "User $USERNAME added Successfully on server"
	else
	Error "Error:" "User $USERNAME could not be added or already exists"
	fi
	sed -i '98i idcadm  ALL=(ALL)  NOPASSWD: ALL' /etc/sudoers
	if [ $? -eq 0 ];then
	echo "SUCCESS:User "$USERNAME" added Successfully on server"
	Success "Success:" "User $USERNAME added Successfully in sudoers file"
	else
	Error "Error:" "User $USERNAME could not be added into sudoers file"
	fi
	elif [ "$USERNAME" == "jioadm" ]
then
	useradd -m -o -u 5001 -d /home/jioadm -p '$6$nFp5GOP1$FwDQPr3D3rHS/VrEiK2YYwODDN3QkEsfZwtjzVbj4k9cLUDbiV2fV2Itzh9FB35RRhaheOdtQ3ylMSvVdyXPl/' jioadm
	if [ $? -eq 0 ];then
	echo "SUCCESS:User "$USERNAME" added Successfully on server"
	Success "Success:" "User $USERNAME added Successfully on server"
	else
	Error "Error:" "User $USERNAME could not be added or already exists"
	fi
	sed -i '98i jioadm ALL=(ALL)  NOPASSWD: ALL' /etc/sudoers
	if [ $? -eq 0 ];then
	Success "Success:" "User $USERNAME added Successfully in sudoers file"
	else
	Error "Error:" "User $USERNAME could not be added into sudoers file or already exists"
	fi
	elif [ "$USERNAME" == "pimadm" ]
then
	useradd -m -o -u 5002 -d /home/pimadm -p '$6$l0rkhxdN$bDsinQjlaB8VQbn/pDpXEslPMwrNXrZBD/Tq4jen7A82JvpF02zFvk8toNUHeXRiAKvpUrzWNKMhojxdGiLQr0' pimadm
	if [ $? -eq 0 ];then
	echo "SUCCESS:User "$USERNAME" added Successfully on server"
	Success "Success:" "User $USERNAME added Successfully on server"
	else
	Error "Error:" "User $USERNAME could not be added"
	fi
	sed -i '98i pimadm  ALL=(ALL)  NOPASSWD: ALL' /etc/sudoers
	if [ $? -eq 0 ];then
	Success "Success:" "User $USERNAME added Successfully in sudoers file"
	else
	Error "Error:" "User $USERNAME could not be added into sudoers file"
	fi
	elif [ "$USERNAME" == "jiouser" ]
then
	useradd -m -o -u 5003 -d /home/jiouser -p '$6$tjzIYIak$psWHIGIwfZGIOXJPSiHHe9fRXFIBi8T455ZIbFF10QYdo4tu0r7NuIgL.E2tHhuPkwXMErLGOBwbrG18FYEEa1' jiouser
	if [ $? -eq 0 ];then
	echo "SUCCESS:User "$USERNAME" added Successfully on server"
	Success "Success:" "User $USERNAME added Successfully on server"
	else
	Error "Error:" "User $USERNAME could not be added"
	sed -i '98i jiouser  ALL=(ALL)  NOPASSWD: ALL' /etc/sudoers
	if [ $? -eq 0 ];then
	Success "Success:" "User $USERNAME added Successfully in sudoers file"
	else
	Error "Error:" "User $USERNAME could not be added into sudoers file"
	fi
fi
fi
}

compute_rhel6_crash_kernel ()
{
    reserved_memory=128
    mem_size=$1
    kernel_subversion='uname -r|awk -F"." '{print $3}'|awk -F"-" '{print $2}''
    if [ $kernel_subversion -lt 220 ] ; then
        if [ $mem_size -le 2 ]
        then
            reserved_memory=128
        elif [ $mem_size -le 6 ]
        then
            reserved_memory=256
        elif [ $mem_size -le 8 ]
        then
            reserved_memory=512
        else
            reserved_memory=768
        fi
        Success "INFO:" ""$reserved_memory"M"
    fi

    if [ $kernel_subversion -ge 220 ] && [ $kernel_subversion -lt 279 ]; then # Check for kernel version > = 220 and RAM > = 4 GiB
    if [ $mem_size -ge 4 ];then
        reserved_memory="auto"
        echo "$reserved_memory"
    else # Check for kernel version > = 220 and RAM < 4 GiB
        reserved_memory=128
        Success "INFO:" ""$reserved_memory"M"
    fi
    fi

    if [ $kernel_subversion -ge 279 ] ; then   # Check for kernel version > = 279 and RAM > = 2 GiB
    if [ $mem_size -ge 2 ]
    then
        reserved_memory="auto"
        echo "$reserved_memory"
    else # Check for kernel version > = 279 and RAM < 2 GiB
    reserved_memory=128
    Success "INFO:" ""$reserved_memory"M"
    fi
    fi
}

#############Log Files Check################################################
if [ -d $LOG_DIR ];then
   echo "Success:" "The log directory "$LOG_DIR" already exist so no need to create"
   Success "Sucess:" "The log directory "$LOG_DIR" already exist so no need to create"

   else
   echo "INFO:The log directory "$LOG_DIR" does not exist so creating the log dir:"$LOG_DIR""
   Error "INFO:" "The log directory "$LOG_DIR" does not exist so creating the log dir:"$LOG_DIR""
   mkdir -p $LOG_DIR
   if [ $? -eq 0 ];then
   echo "SUCCESS "$LOG_DIR" created successfully"
   Success "Success:" ""$LOG_DIR" created successfully"
   else
   echo "ERROR:Unable to create "$LOG_DIR":something went wrong"
   Error "Error:" "Unable to create "$LOG_DIR":something went wrong"
   fi
fi

if [ -f $LOG_FILE ];then
   echo "INFO:The log directory "$LOG_FILE" already exist so no need to create"
   Success "INFO:" "The log file "$LOG_FILE" already exist so no need to create"
   else
   echo "INFO:The log directory "$LOG_FILE" does not exist so creating the log dir:"$LOG_FILE""
   Success "Info:" "The log directory "$LOG_FILE" does not exist so creating the log dir:"$LOG_FILE""
   
   touch $LOG_FILE
   if [ $? -eq 0 ];then
   echo "SUCCESS:"$LOG_FILE" created successfully"
   Success "Success:" ""$LOG_FILE" created successfully"
   else
   echo "ERROR:Unable to create "$LOG_FILE":something went wrong"
   Error "Error:" "Unable to create "$LOG_FILE":something went wrong"
   fi
fi

##################Main Code Starts Here#######################################
if grep -q -i "release 6" /etc/redhat-release
then
  echo "INFO:running RHEL/CentOS 6.x"
  ###########changing contents in rsyslog file for RHEL6########################
  if [ -f $Rsyslog_File ];then
   echo "Success: "$Rsyslog_File" exists,proceeding to change the file"
   Success "Success:" ""$Rsyslog_File" exists,proceeding to change the file"
   echo "##############Changing rsyslog file on the server####################"
   if grep -q  $PATTERN_RSYSLOG "$Rsyslog_File" ;then
   echo "INFO:Rsyslog File already have the desired value"
   Success "INFO:" "Rsyslog File already have the desired value"
   else 
   echo "*.*     @REMSTLOG.CLMS.JIO.COM:514" | tee -a $Rsyslog_File
   Check_Pattern "$PATTERN_RSYSLOG" $Rsyslog_File
   fi
   else
   echo "INFO:"$Rsyslog_File" does not exist on Server"
  fi
else
    echo "INFO:running RHEL/CentOS 5.x"
    RSYSLOG_FILE_RHEL5="/etc/syslog.conf"
   if [ -f $RSYSLOG_FILE_RHEL5 ]
   then
   echo "Success: "$RSYSLOG_FILE_RHEL5" exists,proceeding to change the file"
   Success "Success:" ""$RSYSLOG_FILE_RHEL5" exists,proceeding to change the file"
   echo "##############Changing rsyslog file on the server####################"
   if grep -q  $PATTERN_RSYSLOG "$RSYSLOG_FILE_RHEL5"
   then
   echo "INFO:Syslog File already have the desired value"
   Success "INFO:" "Syslog File already have the desired value"
   else
   echo "*.*     @REMSTLOG.CLMS.JIO.COM:514" | tee -a $RSYSLOG_FILE_RHEL5
   Check_Pattern "$PATTERN_RSYSLOG" $RSYSLOG_FILE_RHEL5
   fi
   else
   echo "INFO:"$RSYSLOG_FILE_RHEL5" does not exist on server"
   fi
fi

############Changing Contents for ntpd file######################################
if [ -f $NTPD_FILE ];then
   echo "Success: "$NTPD_FILE" exists,proceeding to change the file"
   Success "Success:" ""$NTPD_FILE" exists,proceeding to change the file"
   echo "##############Changing "$NTPD_FILE" file on the server####################"
   echo $NTPD_CMD
   Check_Pattern "$PATTERN_NTPD" $NTPD_FILE
else
   echo "INFO:"$NTPD_FILE" does not exist on server"
fi

###########Changing Contents for ntpdate file#################################
if grep -q -i "release 6" /etc/redhat-release
then
  echo "running RHEL/CentOS 6.x"
  if [ -f $NTPDATE_FILE ];then
   echo "Success: "$NTPDATE_FILE" exists,proceeding to change the file"
   Success "Success:" ""$NTPDATE_FILE" exists,proceeding to change the file"
   echo "##############Changing "$NTPDATE_FILE" file on the server####################"
   echo $NTPDATE_CMD
   Check_Pattern "$PATTERN_NTDATE" $NTPDATE_FILE
  else
   echo "INFO:File "$NTPDATE_FILE" does not exist on server"
  fi
else
  echo "running RHEL/CentOS 5.x"
  if [ -f $NTPDATE_FILE_RHEL5 ];then
   echo "Success: "$NTPDATE_FILE_RHEL5" exists,proceeding to change the file"
   Success "Success:" ""$NTPDATE_FILE_RHEL5" exists,proceeding to change the file"
   echo "##############Changing "$NTPDATE_FILE_RHEL5" file on the server####################"
   echo $NTPDATE_CMD_RHEL5
   Check_Pattern "$PATTERN_NTDATE" $NTPDATE_FILE_RHEL5
  else
   echo "INFO:File "$NTPDATE_FILE_RHEL5" does not exist on server"
  fi
fi 

########Enabeling kdump on the server#################################################
#######################Start################################
echo "INFO:Kdump Helper is starting to configure kdump service"
Success "INFO:" "Kdump Helper is starting to configure kdump service"
#kexec-tools checking
if ! rpm -q kexec-tools > /dev/null
then 
    echo "INFO:kexec-tools not found, please run command yum install kexec-tools to install it"
	Success "INFO:" "kexec-tools not found, please run command yum install kexec-tools to install it"
    ##exit 1
##fi
else
mem_total='free -g |awk 'NR==2 {print $2 }''
Success "INFO:" "Your total memory is "$mem_total" G"
#backup grub.conf
grub_conf=/boot/grub/grub.conf
grub_conf_kdumphelper=/boot/grub/grub.conf.kdumphelper.$(date +%y-%m-%d-%H:%M:%S)
Success "INFO:" "Backup $grub_conf to $grub_conf_kdumphelper"
cp $grub_conf $grub_conf_kdumphelper
#     RHEL6 crashkernel compute
#     /*
#       https://access.redhat.com/site/solutions/59432
#
crashkernel_para='compute_rhel6_crash_kernel $mem_total '
echo crashkernel=$crashkernel_para is set in $grub_conf
grubby --update-kernel=DEFAULT --args=crashkernel=$crashkernel_para
#backup kdump.conf
kdump_conf=/etc/kdump.conf
kdump_conf_kdumphelper=/etc/kdump.conf.kdumphelper.$(date +%y-%m-%d-%H:%M:%S)
Success "INFO:" "backup "$kdump_conf" to "$kdump_conf_kdumphelper""
cp $kdump_conf $kdump_conf_kdumphelper
#dump_path=/var/crash
dump_path=/opt/Joel/crash
echo path $dump_path > $kdump_conf
dump_level=31
echo core_collector makedumpfile -c --message-level 1 -d $dump_level >> $kdump_conf
echo 'default reboot' >>  $kdump_conf

#enable kdump service
echo "Enabeling kdump service on for 3 and 5 run levels"
#service kdump start
chkconfig kdump on --level 35
chkconfig --list|grep kdump
/etc/init.d/kdump restart
#kernel parameter change
Success "INFO:" "Starting to Configure extra diagnostic options"
sysctl_conf=/etc/sysctl.conf
sysctl_conf_kdumphelper=/etc/sysctl.conf.kdumphelper.$(date +%y-%m-%d-%H:%M:%S)
Success "INFO:" "backup "$sysctl_conf" to "$sysctl_conf_kdumphelper""
cp $sysctl_conf $sysctl_conf_kdumphelper
#server hang
sed -i '/^kernel.sysrq/ s/kernel/#kernel/g ' $sysctl_conf 
echo >> $sysctl_conf
echo '#Panic on sysrq and nmi button, magic button alt+printscreen+c or nmi button could be pressed to collect a vmcore' >> $sysctl_conf
echo '#Added by kdumphelper, more information about it can be found in solution below' >> $sysctl_conf
echo '#https://access.redhat.com/site/solutions/2023' >> $sysctl_conf
echo 'kernel.sysrq=1' >> $sysctl_conf
echo 'kernel.sysrq=1 set in /etc/sysctl.conf'
echo '#https://access.redhat.com/site/solutions/125103' >> $sysctl_conf
echo 'kernel.unknown_nmi_panic=1' >> $sysctl_conf
echo 'kernel.unknown_nmi_panic=1  set in /etc/sysctl.conf'
#softlockup
sed -i '/^kernel.softlockup_panic/ s/kernel/#kernel/g ' $sysctl_conf 
echo >> $sysctl_conf
echo '#Panic on soft lockups.' >> $sysctl_conf
echo '#Added by kdumphelper, more information about it can be found in solution below' >> $sysctl_conf
echo '#https://access.redhat.com/site/solutions/19541' >> $sysctl_conf
echo 'kernel.softlockup_panic=1' >> $sysctl_conf
echo 'kernel.softlockup_panic=1 set in /etc/sysctl.conf'
#oom
sed -i '/^kernel.panic_on_oom/ s/kernel/#kernel/g ' $sysctl_conf 
echo >> $sysctl_conf
echo '#Panic on out of memory.' >> $sysctl_conf
echo '#Added by kdumphelper, more information about it can be found in solution below' >> $sysctl_conf
echo '#https://access.redhat.com/site/solutions/20985' >> $sysctl_conf
echo 'vm.panic_on_oom=1' >> $sysctl_conf
echo 'vm.panic_on_oom=1 set in /etc/sysctl.conf'
fi
#########Disable iptables##############################################################
/etc/init.d/iptables save
echo "INFO:Saving iptables state"
Success "Success:" "iptables saved Sucessfully"
/etc/init.d/iptables stop
if [ $? -eq 0 ];then
  echo "SUCCESS:iptables Disabled Succesfully"
  Success "Success:" "iptables Disabled Succesfully"
  /sbin/chkconfig iptables off
  else
  echo "INFO:Unable to disable iptables"
  Error "INFO:" "Unable to disable iptables"
fi  

########Check Selinux and disable#########################################################
Status='grep -i "SELINUX=disabled" /etc/selinux/config|awk -F = '{print $2}''
if [ "$Status" == "disabled" ];then
   echo "INFO:Selinux is already disabled"
   else
   selinux="/etc/selinux/config"
   sed -i 's/^SELINUX=.*/SELINUX=disabled/g' $selinux
   Setenforce 0
   PATTERN_SELINUX="SELINUX=disabled"
   Check_Pattern "$PATTERN_SELINUX" $selinux
fi
########Disabling NTP Reflection Attack#################################################
NTPCONF="/etc/ntp.conf"
grep -i "disable monitor" /etc/ntp.conf | tee $CHECKSIZE
if [ -s $CHECKSIZE ];then
   echo "Success:The parameter disable monitor is already present in the file hence skipping"
   Success "Success:" "The parameter disable monitor is already present in the file hence skipping"
   else
   echo "disable monitor" | tee -a $NTPCONF
   PATTERN_NTPCONF="disable monitor"
   Check_Pattern "$PATTERN_NTPCONF" $NTPCONF
fi
########Adding Users###################################################################
Check_User idcadm
Check_User jioadm
Check_User pimadm
Check_User jiouser

########### Stopping Avahi Deamon#########################################################
service avahi-daemon stop 2>/dev/null
if [ $? -eq 0 ];then
  echo "Success:avahi deamon disabled Succesfully"
  Success "Success:" "avahi deamon disabled Succesfully"
  /sbin/chkconfig avahi-daemon off
  else
  echo "Info:avahi-deamon service does not exist"
  Error "Info:" "avahi-deamon service does not exist"
fi


