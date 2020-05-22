#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This software has been developed by:

    GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

'''
This file contains functions related to the Trimmomatic process used in both console
mode and gui mode.
'''

#-------------------------------------------------------------------------------

import os
import re
import sys

import xbioinfoapp
import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def create_trimmomatic_config_file(experiment_id='exp001', read_dataset_id=xlib.get_uploaded_read_dataset_name(), read_type='PE', file_1_list=['rnaseq-a_1.fastq'], file_2_list=['rnaseq-a_2.fastq']):
    '''
    Create Trimmomatic config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # create the Trimmomatic config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_trimmomatic_config_file())):
            os.makedirs(os.path.dirname(get_trimmomatic_config_file()))
        with open(get_trimmomatic_config_file(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# The files have to be located in the cluster directory {0}/experiment_id/read_dataset_id'.format(xlib.get_cluster_read_dir())))
            file_id.write( '{0}\n'.format('# The experiment_id and read_dataset_id names are fixed in the identification section.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# You can consult the parameters and trimming sets of Trimmomatic and their meaning in http://www.usadellab.org/cms/index.php?page=trimmomatic.'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information identifies the experiment.'))
            file_id.write( '{0}\n'.format('[identification]'))
            file_id.write( '{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write( '{0:<50} {1}\n'.format('read_dataset_id = {0}'.format(read_dataset_id), '# read dataset identification'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information to set the Trimmomatic parameters.'))
            file_id.write( '{0}\n'.format('[Trimmomatic parameters]'))
            file_id.write( '{0:<50} {1}\n'.format('threads = 4', '# number of threads for use'))
            file_id.write( '{0:<50} {1}\n'.format('phred = 64', '# Phred quality score: {0}'.format(get_phred_code_list_text())))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information to set the trimming step values'))
            file_id.write( '{0}\n'.format('[Trimming step values]'))
            file_id.write( '{0:<50} {1}\n'.format('illuminaclip = NONE', '# cutting of adapter and other illumina-specific sequences: $TRIMMOMATIC_PATH/adapters/fastaWithAdaptersEtc:seedMismatches:palindromeClipThreshold:simpleClipThreshold or NONE (do not perform this step'))
            file_id.write( '{0:<50} {1}\n'.format('slidingwindow = NONE', '# sliding window trimming approach: windowSize:requiredQuality or NONE (do not perform this step)'))
            file_id.write( '{0:<50} {1}\n'.format('leading = NONE', '# threshold quality to cut bases off the start of a read (if below) or NONE (do not perform this step)'))
            file_id.write( '{0:<50} {1}\n'.format('trailing = NONE', '# threshold quality to cut bases off the end of a read (if below) or NONE (do not perform this step)'))
            file_id.write( '{0:<50} {1}\n'.format('crop = NONE', '# length to cut the read removing bases from the end  or NONE (do not perform this step)'))
            file_id.write( '{0:<50} {1}\n'.format('headcrop = 12', '# length to cut from the start of the read or NONE (do not perform this step)'))
            file_id.write( '{0:<50} {1}\n'.format('minlen = NONE', '# length to drop the read if it is below or NONE (do not perform this step)'))
            file_id.write( '{0:<50} {1}\n'.format('tophred33 = FALSE', '# convert quality scores to Phred-33: {0}'.format(get_tophredxx_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('tophred64 = FALSE', '# convert quality scores to Phred-64 : {0}'.format(get_tophredxx_code_list_text())))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information to set the performarce order of every step with value'))
            file_id.write( '{0}\n'.format('[Trimming step order]'))
            file_id.write( '{0:<50} {1}\n'.format('order = headcrop', '# if there are more than one step, they have to be separated by commas'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the global information of all libraries.'))
            file_id.write( '{0}\n'.format('[library]'))
            file_id.write( '{0:<50} {1}\n'.format('read_type = {0}'.format(read_type), '# read type: {0}'.format(get_read_type_code_list_text())))
            for i in range(len(file_1_list)):
                file_id.write( '\n')
                if i == 0:
                    file_id.write( '{0}\n'.format('# This section has the information of the first library.'))
                file_id.write( '{0}\n'.format('[library-{0}]'.format(i + 1)))
                file_id.write( '{0:<50} {1}\n'.format('read_file_1 = {0}'.format(os.path.basename(file_1_list[i])), '# name of the read file in SE read type or the + strand read file in PE case'))
                if read_type == 'SE':
                    file_id.write( '{0:<50} {1}\n'.format('read_file_2 = NONE', '# name of the - strand reads file in PE read type or NONE in SE case'))
                elif read_type == 'PE':
                    file_id.write( '{0:<50} {1}\n'.format('read_file_2 = {0}'.format(os.path.basename(file_2_list[i])), '# name of the - strand reads file in PE read type or NONE in SE case'))
                if i == 0:
                    file_id.write( '\n')
                    file_id.write( '{0}\n'.format('# If there are more libraries, you have to repeat the section library-1 with the data of each file.'))
                    file_id.write( '{0}\n'.format('# The section identification has to be library-n (n is an integer not repeated)'))
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_trimmomatic_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_trimmomatic_process(cluster_name, log, function=None):
    '''
    Run a Trimmomatic process.
    '''

    # initialize the control variable
    OK = True

    # get the Trimmomatic option dictionary
    trimmomatic_option_dict = xlib.get_option_dict(get_trimmomatic_config_file())

    # get the experiment identification
    experiment_id = trimmomatic_option_dict['identification']['experiment_id']

    # warn that the log window does not have to be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # check the Trimmomatic config file
    log.write(f'{xlib.get_separator()}\n')
    log.write('Checking the {0} config file ...\n'.format(xlib.get_trimmomatic_name()))
    (OK, error_list) = check_trimmomatic_config_file(strict=True)
    if OK:
        log.write('The file is OK.\n')
    else:
        log.write('*** ERROR: The config file is not valid.\n')
        log.write('Please correct this file or recreate the config files.\n')

    # create the SSH client connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SSH client ...\n')
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name)
        if OK:
            log.write('The SSH client is connected.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # create the SSH transport connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SSH transport ...\n')
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name)
        if OK:
            log.write('The SSH transport is connected.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # create the SFTP client 
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SFTP client ...\n')
        sftp_client = xssh.create_sftp_client(ssh_transport)
        log.write('The SFTP client is connected.\n')

    # warn that the requirements are being verified 
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Checking process requirements ...\n')

    # check the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name)
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # check the Trimmomatic is installed
    if OK:
        (OK, error_list, is_installed) = xbioinfoapp.is_installed_bioconda_package(xlib.get_trimmomatic_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_installed:
                log.write('*** ERROR: {0} is not installed.\n'.format(xlib.get_trimmomatic_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} installation could not be performed.\n'.format(xlib.get_trimmomatic_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_trimmomatic_code())
        command = f'mkdir --parents {current_run_dir}'
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Trimmomatic process script
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process script {0} ...\n'.format(get_trimmomatic_process_script()))
        (OK, error_list) = build_trimmomatic_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Trimmomatic process script to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(get_trimmomatic_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_trimmomatic_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_trimmomatic_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Trimmomatic process script in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_trimmomatic_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_trimmomatic_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Trimmomatic process starter
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process starter {0} ...\n'.format(get_trimmomatic_process_starter()))
        (OK, error_list) = build_trimmomatic_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Trimmomatic process starter to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(get_trimmomatic_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_trimmomatic_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_trimmomatic_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Trimmomatic process starter in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_trimmomatic_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_trimmomatic_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # submit the Trimmomatic process
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_trimmomatic_process_starter())))
        OK = xssh.submit_script(cluster_name, ssh_client, current_run_dir, os.path.basename(get_trimmomatic_process_starter()), log)

    # close the SSH transport connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Closing the SSH transport connection ...\n')
        xssh.close_ssh_transport_connection(ssh_transport)
        log.write('The connection is closed.\n')

    # close the SSH client connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write(f'{xlib.get_separator()}\n')
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def check_trimmomatic_config_file(strict):
    '''
    Check the Trimmomatic config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        trimmomatic_option_dict = xlib.get_option_dict(get_trimmomatic_config_file())
    except Exception as e:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in trimmomatic_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = trimmomatic_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "read_dataset_id"
            run_id = trimmomatic_option_dict.get('identification', {}).get('read_dataset_id', not_found)
            if run_id == not_found:
                error_list.append('*** ERROR: the key "read_dataset_id" is not found in the section "identification".')
                OK = False

        # check section "Trimmomatic parameters"
        if 'Trimmomatic parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Trimmomatic parameters" is not found.')
            OK = False
        else:

            # check section "Trimmomatic parameters" - key "threads"
            threads = trimmomatic_option_dict.get('Trimmomatic parameters', {}).get('threads', not_found)
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "Trimmomatic parameters".')
                OK = False
            elif not xlib.check_int(threads, minimum=1):
                error_list.append('*** ERROR: the key "threads" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Trimmomatic parameters" - key "phred"
            phred = trimmomatic_option_dict.get('Trimmomatic parameters', {}).get('phred', not_found)
            if phred == not_found:
                error_list.append('*** ERROR: the key "phred" is not found in the section "Trimmomatic parameters".')
                OK = False
            elif not xlib.check_code(phred, get_phred_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "phred" has to be {0}.'.format(get_phred_code_list_text()))
                OK = False

        # check section "Trimming step values"
        if 'Trimming step values' not in sections_list:
            error_list.append('*** ERROR: the section "Trimming step values" is not found.')
            OK = False
        else:

            # initialize variable to check that there are tasks select to performe
            selected_step_list = []

            # check section "Trimming step values" - key "illuminaclip"
            illuminaclip = trimmomatic_option_dict.get('Trimming step values', {}).get('illuminaclip', not_found)
            if illuminaclip == not_found:
                error_list.append('*** ERROR: the key "illuminaclip" is not found in the section "Trimming step values".')
                OK = False
            elif illuminaclip.upper() != 'NONE':
                try:
                    pattern = r'^\$TRIMMOMATIC_PATH/adapters/(.+):(.+):(.+):(.+)$'
                    mo = re.search(pattern, illuminaclip)
                    fasta_with_adapters_etc = mo.group(1).strip()
                    seed_mismatches = mo.group(2).strip()
                    palindrome_clip_threshold = mo.group(3).strip()
                    simple_clip_threshold = mo.group(4).strip()
                except Exception as e:
                    error_list.append('*** ERROR: the value of the key "illuminaclip" has to be $TRIMMOMATIC_PATH/adapters/fastaWithAdaptersEtc:seedMismatches:palindromeClipThreshold:simpleClipThreshold or NONE.')
                    OK = False
                else:
                    selected_step_list.append('illuminaclip')

            # check section "Trimming step values" - key "slidingwindow"
            slidingwindow = trimmomatic_option_dict.get('Trimming step values', {}).get('slidingwindow', not_found)
            if slidingwindow == not_found:
                error_list.append('*** ERROR: the key "slidingwindow" is not found in the section "Trimming step values".')
                OK = False
            elif slidingwindow.upper() != 'NONE':
                try:
                    pattern = r'^(.+):(.+)$'
                    mo = re.search(pattern, slidingwindow)
                    window_size = mo.group(1).strip()
                    required_quality = mo.group(2).strip()
                except Exception as e:
                    error_list.append('*** ERROR: the value of the key "slidingwindow" has to be windowSize:requiredQuality or NONE.')
                    OK = False
                else:
                    selected_step_list.append('slidingwindow')

            # check section "Trimming step values" - key "leading"
            leading = trimmomatic_option_dict.get('Trimming step values', {}).get('leading', not_found)
            if leading == not_found:
                error_list.append('*** ERROR: the key "leading" is not found in the section "Trimming step values".')
                OK = False
            elif leading.upper() != 'NONE' and not xlib.check_int(leading, minimum=1):
                error_list.append('*** ERROR: the key "leading" has to be an integer number greater than or equal to 1 or NONE.')
                OK = False
            elif leading.upper() != 'NONE':
                selected_step_list.append('leading')

            # check section "Trimming step values" - key "trailing"
            trailing = trimmomatic_option_dict.get('Trimming step values', {}).get('trailing', not_found)
            if trailing == not_found:
                error_list.append('*** ERROR: the key "trailing" is not found in the section "Trimming step values".')
                OK = False
            elif trailing.upper() != 'NONE' and not xlib.check_int(trailing, minimum=1):
                error_list.append('*** ERROR: the key "trailing" has to be an integer number greater than or equal to 1 or NONE.')
                OK = False
            elif trailing.upper() != 'NONE':
                selected_step_list.append('trailing')

            # check section "Trimming step values" - key "crop"
            crop = trimmomatic_option_dict.get('Trimming step values', {}).get('crop', not_found)
            if crop == not_found:
                error_list.append('*** ERROR: the key "crop" is not found in the section "Trimming step values".')
                OK = False
            elif crop.upper() != 'NONE' and not xlib.check_int(crop, minimum=1):
                error_list.append('*** ERROR: the key "crop" has to be an integer number greater than or equal to 1 or NONE.')
                OK = False
            elif crop.upper() != 'NONE':
                selected_step_list.append('crop')

            # check section "Trimming step values" - key "headcrop"
            headcrop = trimmomatic_option_dict.get('Trimming step values', {}).get('headcrop', not_found)
            if headcrop == not_found:
                error_list.append('*** ERROR: the key "headcrop" is not found in the section "Trimming step values".')
                OK = False
            elif headcrop.upper() != 'NONE' and not xlib.check_int(headcrop, minimum=1):
                error_list.append('*** ERROR: the key "headcrop" has to be an integer number greater than or equal to 1 or NONE.')
                OK = False
            elif headcrop.upper() != 'NONE':
                selected_step_list.append('headcrop')

            # check section "Trimming step values" - key "minlen"
            minlen = trimmomatic_option_dict.get('Trimming step values', {}).get('minlen', not_found)
            if minlen == not_found:
                error_list.append('*** ERROR: the key "minlen" is not found in the section "Trimming step values".')
                OK = False
            elif minlen.upper() != 'NONE' and not xlib.check_int(minlen, minimum=1):
                error_list.append('*** ERROR: the key "minlen" has to be an integer number greater than or equal to 1 or NONE.')
                OK = False
            elif minlen.upper() != 'NONE':
                selected_step_list.append('minlen')

            # check section "Trimming step values" - key "tophred33"
            tophred33 = trimmomatic_option_dict.get('Trimming step values', {}).get('tophred33', not_found)
            if tophred33 == not_found:
                error_list.append('*** ERROR: the key "tophred33" is not found in the section "Trimming step values".')
                OK = False
            elif not xlib.check_code(tophred33, get_tophredxx_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "tophred33" has to be {0}.'.format(get_tophredxx_code_list_text()))
                OK = False
            elif tophred33.upper() == 'TRUE':
                selected_step_list.append('tophred33')

            # check section "Trimming step values" - key "tophred64"
            tophred64 = trimmomatic_option_dict.get('Trimming step values', {}).get('tophred64', not_found)
            if tophred64 == not_found:
                error_list.append('*** ERROR: the key "tophred64" is not found in the section "Trimming step values".')
                OK = False
            elif not xlib.check_code(tophred64, get_tophredxx_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "tophred64" has to be {0}.'.format(get_tophredxx_code_list_text()))
                OK = False
            elif tophred64.upper() == 'TRUE':
                selected_step_list.append('tophred64')

            # check that there are tasks select to performe
            if tophred33.upper() == 'TRUE' and tophred64.upper() == 'TRUE':
                error_list.append('*** ERROR: both tophred33 as tophred64 have value TRUE.')
                OK = False

            # check that there are tasks select to performe
            if selected_step_list == []:
                error_list.append('*** ERROR: in the section "Trimming step values" there are not steps selected to performe.')
                OK = False

        # check section "Trimming step order"
        if 'Trimming step order' not in sections_list:
            error_list.append('*** ERROR: the section "Trimming step order" is not found.')
            OK = False
        else:

            # check section "Trimming step order" - key "order"
            order = trimmomatic_option_dict.get('Trimming step order', {}).get('order', not_found)
            if order == not_found:
                error_list.append('*** ERROR: the key "order" is not found in the section "Trimming step order".')
                OK = False
            else:
                ordered_step_list = xlib.split_literal_to_string_list(order)
                if ordered_step_list == []:
                    error_list.append('*** ERROR: the key "order" is not a valid step list.')
                    OK = False
                else:
                    for ordered_step in ordered_step_list:
                        value = trimmomatic_option_dict.get('Trimming step values', {}).get(ordered_step, not_found)
                        if value == not_found:
                            error_list.append('*** ERROR: the step {0} in the section "Trimming step order" is a invalid step.'.format(ordered_step))
                            OK = False
                        elif value.upper() in ['NONE', 'FALSE']:
                            error_list.append('*** ERROR: the step {0} is in section "Trimming step order" but it does not have value in the section "Trimming step values".'.format(ordered_step))
                            OK = False
                    for selected_step in selected_step_list:
                        if selected_step not in ordered_step_list:
                            error_list.append('*** ERROR: the step {0} in the section "Trimming step values" has value but it is not in in section "Trimming step order".'.format(selected_step))
                            OK = False

        # check section "library"
        if 'library' not in sections_list:
            error_list.append('*** ERROR: the section "library" is not found.')
            OK = False
        else:

            # check section "library" - key "read_type"
            read_type = trimmomatic_option_dict.get('library', {}).get('read_type', not_found)
            if read_type == not_found:
                error_list.append('*** ERROR: the key "read_type" is not found in the section "library".')
                OK = False
            elif not xlib.check_code(read_type, get_read_type_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "read_type" has to be {0}.'.format(get_read_type_code_list_text()))
                OK = False

        # check section "library-1"
        if 'library-1' not in sections_list:
            error_list.append('*** ERROR: the section "library-1" is not found.')
            OK = False

        # check all sections "library-n"
        for section in sections_list:

            if section not in ['identification', 'Trimmomatic parameters', 'Trimming step values', 'Trimming step order', 'library']:

                # check than the section identification is like library-n 
                if not re.match('^library-[0-9]+$', section):
                    error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                    OK = False

                else:

                    # check section "library-n" - key "readsfile1"
                    read_file_1 = trimmomatic_option_dict.get(section, {}).get('read_file_1', not_found)
                    if read_file_1 == not_found:
                        error_list.append('*** ERROR: the key "read_file_1" is not found in the section "{0}"'.format(section))
                        OK = False

                    # check section "library-n" - key "read_file_2"
                    read_file_2 = trimmomatic_option_dict.get(section, {}).get('read_file_2', not_found)
                    if read_file_2 == not_found:
                        error_list.append('*** ERROR: the key "read_file_2" is not found in the section "{0}"'.format(section))
                        OK = False

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_trimmomatic_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_trimmomatic_process_script(cluster_name, current_run_dir):
    '''
    Build the current Trimmomatic process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the Trimmomatic option dictionary
    trimmomatic_option_dict = xlib.get_option_dict(get_trimmomatic_config_file())

    # get the options
    experiment_id = trimmomatic_option_dict['identification']['experiment_id']
    read_dataset_id = trimmomatic_option_dict['identification']['read_dataset_id']
    read_type = trimmomatic_option_dict['library']['read_type'].upper()
    threads = trimmomatic_option_dict['Trimmomatic parameters']['threads']
    phred = trimmomatic_option_dict['Trimmomatic parameters']['phred']

    # build the step dictionary
    step_dict = {}
    step_dict['illuminaclip'] = trimmomatic_option_dict['Trimming step values']['illuminaclip']
    step_dict['slidingwindow'] = trimmomatic_option_dict['Trimming step values']['slidingwindow']
    step_dict['leading'] = trimmomatic_option_dict['Trimming step values']['leading']
    step_dict['trailing'] = trimmomatic_option_dict['Trimming step values']['trailing']
    step_dict['crop'] = trimmomatic_option_dict['Trimming step values']['crop']
    step_dict['headcrop'] = trimmomatic_option_dict['Trimming step values']['headcrop']
    step_dict['minlen'] = trimmomatic_option_dict['Trimming step values']['minlen']
    step_dict['tophred33'] = trimmomatic_option_dict['Trimming step values']['tophred33']
    step_dict['tophred64'] = trimmomatic_option_dict['Trimming step values']['tophred64']

    # get the ordered step list
    ordered_step_list = xlib.split_literal_to_string_list(trimmomatic_option_dict['Trimming step order']['order'])

    # build the selected steps with their values
    selected_steps = ''
    for ordered_step in ordered_step_list:
        step_value = step_dict[ordered_step]
        if ordered_step not in ['tophred33', 'tophred64']:
            selected_steps += '{0}:{1} '.format(ordered_step.upper(), step_value)
        else:
            selected_steps += '{0} '.format(ordered_step.upper())

    # get the sections list
    sections_list = []
    for section in trimmomatic_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build the file name list
    read_file_1_list = []
    read_file_2_list = []
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^library-[0-9]+$', section):
            read_file_1 = trimmomatic_option_dict[section]['read_file_1']
            read_file_1_list.append(read_file_1)
            if read_type.upper() == 'PE':
                read_file_2 = trimmomatic_option_dict[section]['read_file_2']
                read_file_2_list.append(read_file_2)

    # get the input read directory
    input_read_dir = xlib.get_cluster_experiment_read_dataset_dir(experiment_id, read_dataset_id)

    # get the output read directory
    output_read_dir = xlib.get_cluster_experiment_read_dataset_dir(experiment_id, os.path.basename(current_run_dir))

    # write the Trimmomatic process script
    try:
        if not os.path.exists(os.path.dirname(get_trimmomatic_process_script())):
            os.makedirs(os.path.dirname(get_trimmomatic_process_script()))
        with open(get_trimmomatic_process_script(), mode='w', encoding='iso-8859-1', newline='\n') as script_file_id:
            script_file_id.write( '#!/bin/bash\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'SEP="#########################################"\n')
            script_file_id.write( 'export HOST_IP=`curl --silent checkip.amazonaws.com`\n')
            script_file_id.write( 'export HOST_ADDRESS="ec2-${HOST_IP//./-}-compute-1.amazonaws.com"\n')
            script_file_id.write( '{0}\n'.format('TRIMMOMATIC_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_trimmomatic_bioconda_code())))
            script_file_id.write( '{0}\n'.format('PATH=$TRIMMOMATIC_PATH:$PATH'))
            script_file_id.write( '{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            script_file_id.write( '{0}\n'.format('source activate {0}'.format(xlib.get_trimmomatic_bioconda_code())))
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('STATUS_DIR={0}'.format(xlib.get_status_dir(current_run_dir))))
            script_file_id.write( '{0}\n'.format('SCRIPT_STATUS_OK={0}'.format(xlib.get_status_ok(current_run_dir))))
            script_file_id.write( '{0}\n'.format('SCRIPT_STATUS_WRONG={0}'.format(xlib.get_status_wrong(current_run_dir))))
            script_file_id.write( '{0}\n'.format('mkdir --parents $STATUS_DIR'))
            script_file_id.write( '{0}\n'.format('if [ -f $SCRIPT_STATUS_OK ]; then rm $SCRIPT_STATUS_OK; fi'))
            script_file_id.write( '{0}\n'.format('if [ -f $SCRIPT_STATUS_WRONG ]; then rm $SCRIPT_STATUS_WRONG; fi'))
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function init\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    INIT_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "Script started at $FORMATTED_INIT_DATETIME+00:00."\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write(f'    echo "CLUSTER: {cluster_name}"\n')
            script_file_id.write(f'    echo "HOST_IP: $HOST_IP - HOST_ADDRESS: $HOST_ADDRESS"\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function run_trimmomatic_process'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    mkdir --parents {0}'.format(output_read_dir)))
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('     echo "Trimmomatic v`trimmomatic -version`"'))
            for i in range(len(read_file_1_list)):
                # get the unpaired read file names
                if read_file_1_list[i].endswith('.gz'):
                    unpaired_read_file_1 = '{0}.unpaired.gz'.format(read_file_1_list[i][:-3])
                else:
                    unpaired_read_file_1 = '{0}.unpaired'.format(read_file_1_list[i])
                if read_file_2_list[i].endswith('.gz'):
                    unpaired_read_file_2 = '{0}.unpaired.gz'.format(read_file_2_list[i][:-3])
                else:
                    unpaired_read_file_2 = '{0}.unpaired'.format(read_file_2_list[i])
                # write the trimmomatic run instructions
                script_file_id.write( '    echo "$SEP"\n')
                script_file_id.write( '{0}\n'.format('    /usr/bin/time \\'))
                script_file_id.write( '{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
                script_file_id.write( '{0}\n'.format('        trimmomatic \\'))
                script_file_id.write( '{0}\n'.format('            {0} \\'.format(read_type)))
                script_file_id.write( '{0}\n'.format('            -threads {0} \\'.format(threads)))
                script_file_id.write( '{0}\n'.format('            -phred{0} \\'.format(phred)))
                script_file_id.write( '{0}\n'.format('            -trimlog {0}.log \\'.format(read_file_1_list[i])))
                if read_type == 'SE':
                    script_file_id.write( '{0}\n'.format('            {0}/{1} \\'.format(input_read_dir, read_file_1_list[i])))
                    script_file_id.write( '{0}\n'.format('            {0}/{1} \\'.format(output_read_dir, read_file_1_list[i])))
                elif read_type == 'PE':
                    script_file_id.write( '{0}\n'.format('            {0}/{1} \\'.format(input_read_dir, read_file_1_list[i])))
                    script_file_id.write( '{0}\n'.format('            {0}/{1} \\'.format(input_read_dir, read_file_2_list[i])))
                    script_file_id.write( '{0}\n'.format('            {0}/{1} \\'.format(output_read_dir, read_file_1_list[i])))
                    script_file_id.write( '{0}\n'.format('            {0}/{1} \\'.format(output_read_dir, unpaired_read_file_1)))
                    script_file_id.write( '{0}\n'.format('            {0}/{1} \\'.format(output_read_dir, read_file_2_list[i])))
                    script_file_id.write( '{0}\n'.format('            {0}/{1} \\'.format(output_read_dir, unpaired_read_file_2)))
                script_file_id.write( '{0}\n'.format('            {0}'.format(selected_steps)))
                script_file_id.write( '{0}\n'.format('    RC=$?'))
                script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error trimmomatic $RC; fi'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function end'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            script_file_id.write( '{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            script_file_id.write( '{0}\n'.format('    calculate_duration'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Script ended OK at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            script_file_id.write( '{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_trimmomatic_name())))
            script_file_id.write( '{0}\n'.format('    MESSAGE="{0}"'.format(xlib.get_mail_message_ok(xlib.get_trimmomatic_name(), cluster_name))))
            script_file_id.write( '    mail --append "Content-type: text/html;" --append "FROM:root@NGScloud2" --subject="$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"\n')
            script_file_id.write( '{0}\n'.format('    touch $SCRIPT_STATUS_OK'))
            script_file_id.write( '{0}\n'.format('    exit 0'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function manage_error'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            script_file_id.write( '{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            script_file_id.write( '{0}\n'.format('    calculate_duration'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "ERROR: $1 returned error $2"'))
            script_file_id.write( '{0}\n'.format('    echo "Script ended WRONG at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            script_file_id.write( '{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_trimmomatic_name())))
            script_file_id.write( '{0}\n'.format('    MESSAGE="{0}"'.format(xlib.get_mail_message_wrong(xlib.get_trimmomatic_name(), cluster_name))))
            script_file_id.write( '    mail --append "Content-type: text/html;" --append "FROM:root@NGScloud2" --subject="$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"\n')
            script_file_id.write( '{0}\n'.format('    touch $SCRIPT_STATUS_WRONG'))
            script_file_id.write( '{0}\n'.format('    exit 3'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function calculate_duration\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    DURATION=`expr $END_DATETIME - $INIT_DATETIME`\n')
            script_file_id.write( '    HH=`expr $DURATION / 3600`\n')
            script_file_id.write( '    MM=`expr $DURATION % 3600 / 60`\n')
            script_file_id.write( '    SS=`expr $DURATION % 60`\n')
            script_file_id.write( '    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'init\n')
            script_file_id.write( '{0}\n'.format('run_trimmomatic_process'))
            script_file_id.write( 'end\n')
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_trimmomatic_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_trimmomatic_process_starter(current_run_dir):
    '''
    Build the starter of the current Trimmomatic process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Trimmomatic process starter
    try:
        if not os.path.exists(os.path.dirname(get_trimmomatic_process_starter())):
            os.makedirs(os.path.dirname(get_trimmomatic_process_starter()))
        with open(get_trimmomatic_process_starter(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '{0}\n'.format('#!/bin/bash'))
            file_id.write( '{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write( '{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_trimmomatic_process_script()), xlib.get_cluster_log_file())))
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_trimmomatic_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_trimmomatic_config_file():
    '''
    Get the Trimmomatic config file path.
    '''

    # assign the Trimmomatic config file path
    trimmomatic_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_trimmomatic_code())

    # return the Trimmomatic config file path
    return trimmomatic_config_file

#-------------------------------------------------------------------------------

def get_trimmomatic_process_script():
    '''
    Get the Trimmomatic process script path in the local computer.
    '''

    # assign the Trimmomatic script path
    trimmomatic_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_trimmomatic_code())

    # return the Trimmomatic script path
    return trimmomatic_process_script

#-------------------------------------------------------------------------------

def get_trimmomatic_process_starter():
    '''
    Get the Trimmomatic process starter path in the local computer.
    '''

    # assign the Trimmomatic process starter path
    trimmomatic_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_trimmomatic_code())

    # return the Trimmomatic starter path
    return trimmomatic_process_starter

#-------------------------------------------------------------------------------
    
def get_phred_code_list():
    '''
    Get the code list of "phred".
    '''

    return ['33', '64']

#-------------------------------------------------------------------------------
    
def get_phred_code_list_text():
    '''
    Get the code list of "format" as text.
    '''

    return '33 (Phred-33) or 64 (Phred-64)'

#-------------------------------------------------------------------------------
    
def get_tophredxx_code_list():
    '''
    Get the code list of "tophred33" or "tophred64".
    '''

    return ['TRUE', 'FALSE']

#-------------------------------------------------------------------------------
    
def get_tophredxx_code_list_text():
    '''
    Get the code list of "tophred33" or "tophred64" as text.
    '''

    return 'TRUE to performance this step, else FALSE'

#-------------------------------------------------------------------------------
    
def get_read_type_code_list():
    '''
    Get the code list of "read_type".
    '''

    return ['SE', 'PE']

#-------------------------------------------------------------------------------
    
def get_read_type_code_list_text():
    '''
    Get the code list of "read_type" as text.
    '''

    return 'SE (single-end) or PE (pair-end)'

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the Trimmomatic process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------