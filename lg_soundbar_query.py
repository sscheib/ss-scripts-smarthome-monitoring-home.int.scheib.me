#!/usr/bin/env python3
import temescal
import logging
import sys
import argparse
import textwrap
import os
from pprint import pprint

RELEVANT_FIELDS = {
    'MAC_INFO_DEV': ['s_wired_mac', 's_wireless_mac', 's_bt_mac'],
    'MEM_MON_DEV': ['i_free_drop', 'i_free_reboot', 'i_load', 'i_total', 'i_buffers', 'i_free', 'i_cache', 'i_warn', 'i_limit'],
    'C4A_SETTING_INFO': ['s_timezone'],
    'BUILD_INFO_DEV': ['i_beta', 'i_package_ver', 's_platform', 's_lgcode', 's_package', 's_dsp', 's_c4a', 's_hdmi', 's_lgrev',
                   's_time', 's_main', 's_micom', 's_rear_rx', 's_rear_tx', 's_woofer_rx', 's_woofer_tx', 's_meq', 's_peq'], 
    'UPDATE_VIEW_INFO': '' # UPDATE_VIEW_INFO has nested fields and thus a special treatment in the callback routine
}

def callback(data):
    pprint(data)
    if data['msg'] not in RELEVANT_FIELDS:
        return

    for name, value in data['data'].items():
        if name not in RELEVANT_FIELDS[data['msg']] and data['msg'] != 'UPDATE_VIEW_INFO':
            continue

        if data['msg'] == 'UPDATE_VIEW_INFO':
            if isinstance(value, dict):
                for nested_name, nested_value in value.items():
                    # if values are empty zabbix_sender expects the value to be "" if the value is actually empty (for strings [starting with s in their name)
                    # and 0 for boolean or integers (which is the other case) in order to get processed properly
                    if not nested_value:
                        if nested_name.startswith('s'):
                            nested_value = '\"\"'
                        else:
                            nested_value = 0

                    cmd = "echo '- {}' | zabbix_sender -i - -c /etc/zabbix/zabbix_agentd.conf".format(data['msg'].lower() + '[' + name + '__' + nested_name + '] ' + str(nested_value))
                    print(cmd)
                    retvalue = os.system(cmd)
                    if retvalue != 0:
                        print('ERROR: Submitting the last values to the Zabbix server for the item failed')
                        sys.exit(1)
                    
        else:
            # if values are empty zabbix_sender expects the value to be "" if the value is actually empty (for strings [starting with s in their name)
            # and 0 for boolean or integers (which is the other case) in order to get processed properly
            if not value:
                if name.startswith('s'):
                    value = '\"\"'
                else:
                    value = 0

            cmd = "echo '- {}' | zabbix_sender -i - -c /etc/zabbix/zabbix_agentd.conf".format(data['msg'].lower() + '[' + name + '] ' + str(value))
            print(cmd)
            retvalue = os.system(cmd)
            if retvalue != 0:
                print('ERROR: Submitting the last values to the Zabbix server for the item failed')
                sys.exit(1)

def main(args):
    parser = argparse.ArgumentParser(description='Transfer releases from FTP')
    parser.add_argument('--ip', action='store', dest='ip', required=True,
                        help='IP of the LG soundbar')
    parser.add_argument('--endpoint', action='store', dest='endpoint', required=True,
                        choices=['mac_info', 'mem_mon_info', 'info', 'settings', 'product_info',
                                 'c4a_info', 'build_info', 'option_info', 'update_info'],
                        help=textwrap.dedent("""
                        Endpoint of the LG soundbar API to query.
                        Following endpoints are available:
                        endpoint mac_info
                            - s_wired_mac 
                            - s_wireless_mac
                            - s_bt_mac
                            - s_uuid
                        endpoint mem_mon_info
                            - i_free_drop
                            - i_free_reboot
                            - i_load
                            - i_total
                            - i_buffers
                            - i_free
                            - i_cache
                            - i_warn
                            - i_limit
                        endpoint info
                            - b_mute
                            - b_update
                            - i_curr_func
                            - i_vol
                            - i_vol_max
                            - i_vol_min
                            - s_user_name
                        endpoint settings
                            - b_drc
                            - b_auto_vol
                            - b_auto_display
                            - b_auto_power
                            - b_tv_remote
                            - b_conn_bt_limit
                            - b_bt_standby
                            - b_night_mode
                            - i_woofer_max
                            - i_woofer_min
                            - i_woofer_level
                            - i_c4a_sharing
                            - i_av_sync
                            - i_sleep_time
                            - i_curr_eq
                            - s_ipv4_addr
                            - s_user_name
                        endpoint product_info
                            - i_network_type
                            - i_model_no
                            - i_model_type
                        endpoint c4a_info
                            - i_agree
                            - s_timezone
                        endpoint build_info
                            - i_beta
                            - i_package_ver
                            - s_platform 
                            - s_lgcode
                            - s_touch
                            - s_package
                            - s_dsp
                            - s_c4a
                            - s_hdmi
                            - s_lgrev
                            - s_time
                            - s_main
                            - s_micom
                            - s_rear_rx
                            - s_rear_tx
                            - s_woofer_rx
                            - s_woofer_tx
                            - s_meq
                            - s_demo
                            - s_peq
                        endpoint option_info
                            - i_length
                            - s_option
                        """))

    arguments = parser.parse_args()
   
    speaker = temescal.temescal(arguments.ip, callback=callback)
    if arguments.endpoint == 'mac_info':
        speaker.get_mac_info()
    elif arguments.endpoint == 'mem_mon_info':
        speaker.get_mem_mon_info()
    elif arguments.endpoint == 'info':
        speaker.get_info()
    elif arguments.endpoint == 'settings':
        speaker.get_settings()
    elif arguments.endpoint == 'product_info':
        speaker.get_product_info()
    elif arguments.endpoint == 'c4a_info':
        speaker.get_c4a_info()
    elif arguments.endpoint == 'build_info':
        speaker.get_build_info()
    elif arguments.endpoint == 'option_info':
        speaker.get_option_info()
    elif arguments.endpoint == 'update_info':
        speaker.get_update_info()

if __name__ == '__main__':
    main(sys.argv)


#
# DEBUG STUFF 
#
#speaker.get_radio_info() -> NOT SUPPORTED
#speaker.get_ap_info()  -> NOT SUPPORTED
#speaker.get_update_info() -> dict, special treatment
