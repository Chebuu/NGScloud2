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
This file contains functions related to the QUAST process used in both console
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

def create_quast_config_file(experiment_id='exp001', reference_dataset_id='NONE', reference_file='NONE', assembly_dataset_id='sdnt-170101-235959', assembly_type='CONTIGS'):
    '''
    Create QUAST config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # set the app
    if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
        assembly_software = xlib.get_soapdenovotrans_code()
    elif assembly_dataset_id.startswith(xlib.get_transabyss_code()):
        assembly_software = xlib.get_transabyss_code()
    elif assembly_dataset_id.startswith(xlib.get_trinity_code()):
        assembly_software = xlib.get_trinity_code()
    elif assembly_dataset_id.startswith(xlib.get_ggtrinity_code()):
        assembly_software = xlib.get_ggtrinity_code()
    elif assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()):
        assembly_software = xlib.get_cd_hit_est_code()
    elif assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
        assembly_software = xlib.get_transcript_filter_code()

    # create the QUAST config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_quast_config_file())):
            os.makedirs(os.path.dirname(get_quast_config_file()))
        with open(get_quast_config_file(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '# You must review the information of this file and update the values with the corresponding ones to the current run.\n')
            file_id.write( '#\n')
            file_id.write( '{0}\n'.format('# The reference file has to be located in the cluster directory {0}/experiment_id/reference_dataset_id'.format(xlib.get_cluster_reference_dir())))
            file_id.write(f'# The assembly files have to be located in the cluster directory {xlib.get_cluster_result_dir()}/experiment_id/assembly_dataset_id\n')
            file_id.write( '{0}\n'.format('# The experiment_id, reference_dataset_id, reference_file and assembly_dataset_id are fixed in the identification section.'))
            file_id.write( '#\n')
            file_id.write( '{0}\n'.format('# You can consult the parameters of QUAST and their meaning in "http://quast.sourceforge.net/quast.html".'))
            file_id.write( '\n')
            file_id.write( '# This section has the information identifies the experiment.\n')
            file_id.write( '[identification]\n')
            file_id.write( '{0:<50} {1}\n'.format(f'experiment_id = {experiment_id}', '# experiment identification'))
            file_id.write( '{0:<50} {1}\n'.format('reference_dataset_id = {0}'.format(reference_dataset_id), '# reference dataset identification or NONE'))
            file_id.write( '{0:<50} {1}\n'.format('reference_file = {0}'.format(reference_file), '# reference file name or NONE'))
            file_id.write( '{0:<50} {1}\n'.format(f'assembly_software = {assembly_software}', f'# assembly software: {get_assembly_software_code_list_text()}'))
            file_id.write( '{0:<50} {1}\n'.format(f'assembly_dataset_id = {assembly_dataset_id}', '# assembly dataset identification'))
            file_id.write( '{0:<50} {1}\n'.format(f'assembly_type = {assembly_type}', f'# assembly type: CONTIGS or SCAFFOLDS in {xlib.get_soapdenovotrans_name()}; NONE in any other case'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information to set the QUAST parameters'))
            file_id.write( '{0}\n'.format('[QUAST parameters]'))
            file_id.write( '{0:<50} {1}\n'.format('threads = 4', '# number of threads for use'))
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_quast_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_quast_process(cluster_name, log, function=None):
    '''
    Run a QUAST process.
    '''

    # initialize the control variable
    OK = True

    # get the QUAST option dictionary
    quast_option_dict = xlib.get_option_dict(get_quast_config_file())

    # get the experiment identification
    experiment_id = quast_option_dict['identification']['experiment_id']

    # warn that the log window does not have to be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # check the QUAST config file
    log.write(f'{xlib.get_separator()}\n')
    log.write('Checking the {0} config file ...\n'.format(xlib.get_quast_name()))
    (OK, error_list) = check_quast_config_file(strict=True)
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
            log.write(f'*** ERROR: The cluster {cluster_name} is not running. Its state is {master_state_code} ({master_state_name}).\n')
            OK = False

    # check the QUAST is installed
    if OK:
        (OK, error_list, is_installed) = xbioinfoapp.is_installed_anaconda_package(xlib.get_quast_anaconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_installed:
                log.write('*** ERROR: {0} is not installed.\n'.format(xlib.get_quast_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} installation could not be performed.\n'.format(xlib.get_quast_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_quast_code())
        command = f'mkdir --parents {current_run_dir}'
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write(f'The directory path is {current_run_dir}.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the QUAST process script
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process script {0} ...\n'.format(get_quast_process_script()))
        (OK, error_list) = build_quast_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the QUAST process script to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process script {0} to the directory {1} ...\n'.format(get_quast_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_quast_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_quast_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the QUAST process script in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_quast_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_quast_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the QUAST process starter
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process starter {0} ...\n'.format(get_quast_process_starter()))
        (OK, error_list) = build_quast_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the QUAST process starter to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process starter {0} to the directory {1} ...\n'.format(get_quast_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_quast_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_quast_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the QUAST process starter in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_quast_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_quast_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # submit the QUAST process
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_quast_process_starter())))
        OK = xssh.submit_script(cluster_name, ssh_client, current_run_dir, os.path.basename(get_quast_process_starter()), log)

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

def check_quast_config_file(strict):
    '''
    Check the QUAST config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        quast_option_dict = xlib.get_option_dict(get_quast_config_file())
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append('*** ERROR: The option dictionary could not be built from the config file')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in quast_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = quast_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "reference_dataset_id"
            reference_dataset_id = quast_option_dict.get('identification', {}).get('reference_dataset_id', not_found)
            if reference_dataset_id == not_found:
                error_list.append('*** ERROR: the key "reference_dataset_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "reference_file"
            reference_file = quast_option_dict.get('identification', {}).get('reference_file', not_found)
            if reference_file == not_found:
                error_list.append('*** ERROR: the key "reference_file" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "assembly_software"
            assembly_software = quast_option_dict.get('identification', {}).get('assembly_software', not_found)
            if assembly_software == not_found:
                error_list.append('*** ERROR: the key "assembly_software" is not found in the section "identification".')
                OK = False
            elif not xlib.check_code(assembly_software, get_assembly_software_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "assembly_software" has to be {get_assembly_software_code_list_text()}.')
                OK = False

            # check section "identification" - key "assembly_dataset_id"
            assembly_dataset_id = quast_option_dict.get('identification', {}).get('assembly_dataset_id', not_found)
            if assembly_dataset_id == not_found:
                error_list.append('*** ERROR: the key "assembly_dataset_id" is not found in the section "identification".')
                OK = False
            elif not xlib.check_startswith(assembly_dataset_id, get_assembly_software_code_list(), case_sensitive=True):
                error_list.append(f'*** ERROR: the key "assembly_dataset_id" has to start with {get_assembly_software_code_list_text()}.')
                OK = False

            # check section "identification" - key "assembly_type"
            assembly_type = quast_option_dict.get('identification', {}).get('assembly_type', not_found)
            if assembly_type == not_found:
                error_list.append('*** ERROR: the key "assembly_type" is not found in the section "identification".')
                OK = False
            elif assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()) and assembly_type.upper() not in ['CONTIGS', 'SCAFFOLDS'] or \
                not assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()) and assembly_type.upper() != 'NONE':
                    error_list.append(f'*** ERROR: the key "assembly_type" has to be CONTIGS or SCAFFOLDS in {xlib.get_soapdenovotrans_name()} or NONE in any other case.')
                    OK = False

        # check section "QUAST parameters"
        if 'QUAST parameters' not in sections_list:
            error_list.append('*** ERROR: the section "QUAST parameters" is not found.')
            OK = False
        else:

            # check section "QUAST parameters" - key "threads"
            threads = quast_option_dict.get('QUAST parameters', {}).get('threads', not_found)
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "QUAST parameters".')
                OK = False
            elif not xlib.check_int(threads, minimum=1):
                error_list.append('*** ERROR: the key "threads" has to be an integer number greater than or equal to 1.')
                OK = False

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_quast_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_quast_process_script(cluster_name, current_run_dir):
    '''
    Build the current QUAST process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the QUAST option dictionary
    quast_option_dict = xlib.get_option_dict(get_quast_config_file())

    # get the options
    experiment_id = quast_option_dict['identification']['experiment_id']
    reference_dataset_id = quast_option_dict['identification']['reference_dataset_id']
    reference_file = quast_option_dict['identification']['reference_file']
    assembly_software = quast_option_dict['identification']['assembly_software']
    assembly_dataset_id = quast_option_dict['identification']['assembly_dataset_id']
    assembly_type = quast_option_dict['identification']['assembly_type']
    threads = quast_option_dict['QUAST parameters']['threads']

    # set the reference file path
    if reference_dataset_id.upper() != 'NONE':
        reference_file_path = xlib.get_cluster_reference_file(reference_dataset_id, reference_file)

    # set the transcriptome file path
    if assembly_software == xlib.get_soapdenovotrans_code():
        if assembly_type == 'CONTIGS':
            transcriptome_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/{experiment_id}-{assembly_dataset_id}.contig'
        elif  assembly_type == 'SCAFFOLDS':
            transcriptome_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/{experiment_id}-{assembly_dataset_id}.scafSeq'
    elif assembly_software == xlib.get_transabyss_code():
        transcriptome_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/transabyss-final.fa'
    elif assembly_software == xlib.get_trinity_code():
        transcriptome_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/Trinity.fasta'
    elif assembly_software == xlib.get_ggtrinity_code():
        transcriptome_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/Trinity-GG.fasta'
    elif assembly_software == xlib.get_cd_hit_est_code():
        transcriptome_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/clustered-transcriptome.fasta'
    elif assembly_software == xlib.get_transcript_filter_code():
        transcriptome_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/filtered-transcriptome.fasta'

    # get the QUAST process script name
    quast_process_script = get_quast_process_script()

    # write the QUAST process script
    try:
        if not os.path.exists(os.path.dirname(quast_process_script)):
            os.makedirs(os.path.dirname(quast_process_script))
        with open(quast_process_script, mode='w', encoding='iso-8859-1', newline='\n') as script_file_id:
            script_file_id.write( '#!/bin/bash\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'SEP="#########################################"\n')
            script_file_id.write( 'export HOST_IP=`curl --silent checkip.amazonaws.com`\n')
            script_file_id.write( 'export HOST_ADDRESS="ec2-${HOST_IP//./-}-compute-1.amazonaws.com"\n')
            script_file_id.write( 'export AWS_CONFIG_FILE=/home/ubuntu/.aws/config\n')
            script_file_id.write( 'export AWS_SHARED_CREDENTIALS_FILE=/home/ubuntu/.aws/credentials\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write(f'MINICONDA3_BIN_PATH={xlib.get_cluster_app_dir()}/{xlib.get_miniconda3_name()}/bin\n')
            script_file_id.write(f'export PATH=$MINICONDA3_BIN_PATH:$PATH\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write(f'STATUS_DIR={xlib.get_status_dir(current_run_dir)}\n')
            script_file_id.write(f'SCRIPT_STATUS_OK={xlib.get_status_ok(current_run_dir)}\n')
            script_file_id.write(f'SCRIPT_STATUS_WRONG={xlib.get_status_wrong(current_run_dir)}\n')
            script_file_id.write( 'mkdir --parents $STATUS_DIR\n')
            script_file_id.write( 'if [ -f $SCRIPT_STATUS_OK ]; then rm $SCRIPT_STATUS_OK; fi\n')
            script_file_id.write( 'if [ -f $SCRIPT_STATUS_WRONG ]; then rm $SCRIPT_STATUS_WRONG; fi\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function init\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    INIT_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "Script started at $FORMATTED_INIT_DATETIME+00:00."\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write(f'    echo "CLUSTER: {cluster_name}"\n')
            script_file_id.write( '    echo "HOST NAME: $HOSTNAME"\n')
            script_file_id.write( '    echo "HOST IP: $HOST_IP"\n')
            script_file_id.write( '    echo "HOST ADDRESS: $HOST_ADDRESS"\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function run_quast_process'))
            script_file_id.write( '{\n')
            script_file_id.write(f'    source activate {xlib.get_quast_anaconda_code()}\n')
            script_file_id.write(f'    cd {current_run_dir}\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    quast.py --version'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    /usr/bin/time \\\n')
            script_file_id.write(f'        --format="{xlib.get_time_output_format()}" \\\n')
            script_file_id.write( '{0}\n'.format('        quast.py \\'))
            script_file_id.write( '{0}\n'.format('            --threads {0} \\'.format(threads)))
            script_file_id.write( '{0}\n'.format('            --output-dir {0} \\'.format(current_run_dir)))
            if reference_dataset_id.upper() != 'NONE':
                script_file_id.write( '{0}\n'.format('            -R {0} \\'.format(reference_file_path)))
            if assembly_type.upper() == 'SCAFFOLDS':
                script_file_id.write( '{0}\n'.format('            --scaffolds \\'))
            script_file_id.write( '{0}\n'.format('            {0}'.format(transcriptome_file)))
            script_file_id.write( '    RC=$?\n')
            script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error quast.py $RC; fi'))
            script_file_id.write( '    conda deactivate\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function end\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    END_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    calculate_duration\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "Script ended OK at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    send_mail ok\n')
            script_file_id.write( '    touch $SCRIPT_STATUS_OK\n')
            script_file_id.write( '    exit 0\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function manage_error\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    END_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    calculate_duration\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "ERROR: $1 returned error $2"\n')
            script_file_id.write( '    echo "Script ended WRONG at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    send_mail wrong\n')
            script_file_id.write( '    touch $SCRIPT_STATUS_WRONG\n')
            script_file_id.write( '    exit 3\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            process_name = f'{xlib.get_quast_name()} process'
            mail_message_ok = xlib.get_mail_message_ok(process_name, cluster_name)
            mail_message_wrong = xlib.get_mail_message_wrong(process_name, cluster_name)
            script_file_id.write( 'function send_mail\n')
            script_file_id.write( '{\n')
            script_file_id.write(f'    SUBJECT="{xlib.get_project_name()}: {process_name}"\n')
            script_file_id.write( '    if [ "$1" == "ok" ]; then\n')
            script_file_id.write(f'        MESSAGE="{mail_message_ok}"\n')
            script_file_id.write( '    elif [ "$1" == "wrong" ]; then\n')
            script_file_id.write(f'        MESSAGE="{mail_message_wrong}"\n')
            script_file_id.write( '    else\n')
            script_file_id.write( '         MESSAGE=""\n')
            script_file_id.write( '    fi\n')
            script_file_id.write( '    DESTINATION_FILE=mail-destination.json\n')
            script_file_id.write( '    echo "{" > $DESTINATION_FILE\n')
            script_file_id.write(f'    echo "    \\\"ToAddresses\\\":  [\\\"{xconfiguration.get_contact_data()}\\\"]," >> $DESTINATION_FILE\n')
            script_file_id.write( '    echo "    \\\"CcAddresses\\\":  []," >> $DESTINATION_FILE\n')
            script_file_id.write( '    echo "    \\\"BccAddresses\\\":  []" >> $DESTINATION_FILE\n')
            script_file_id.write( '    echo "}" >> $DESTINATION_FILE\n')
            script_file_id.write( '    MESSAGE_FILE=mail-message.json\n')
            script_file_id.write( '    echo "{" > $MESSAGE_FILE\n')
            script_file_id.write( '    echo "    \\\"Subject\\\": {" >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "        \\\"Data\\\":  \\\"$SUBJECT\\\"," >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "        \\\"Charset\\\":  \\\"UTF-8\\\"" >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "    }," >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "    \\\"Body\\\": {" >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "        \\\"Html\\\": {" >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "            \\\"Data\\\":  \\\"$MESSAGE\\\"," >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "            \\\"Charset\\\":  \\\"UTF-8\\\"" >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "        }" >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "    }" >> $MESSAGE_FILE\n')
            script_file_id.write( '    echo "}" >> $MESSAGE_FILE\n')
            script_file_id.write(f'    aws ses send-email --from {xconfiguration.get_contact_data()} --destination file://$DESTINATION_FILE --message file://$MESSAGE_FILE\n')
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
            script_file_id.write( '{0}\n'.format('run_quast_process'))
            script_file_id.write( 'end\n')
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append('*** ERROR: The file {0} can not be created'.format(quast_process_script))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_quast_process_starter(current_run_dir):
    '''
    Build the starter of the current QUAST process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the QUAST process starter
    try:
        if not os.path.exists(os.path.dirname(get_quast_process_starter())):
            os.makedirs(os.path.dirname(get_quast_process_starter()))
        with open(get_quast_process_starter(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '#!/bin/bash\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( '{0}\n'.format('{0}/{1} &>>{0}/{2}'.format(current_run_dir, os.path.basename(get_quast_process_script()), xlib.get_cluster_log_file())))
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_quast_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_quast_config_file():
    '''
    Get the QUAST config file path.
    '''

    # assign the QUAST config file path
    quast_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_quast_code())

    # return the QUAST config file path
    return quast_config_file

#-------------------------------------------------------------------------------

def get_quast_process_script():
    '''
    Get the QUAST process script path in the local computer.
    '''

    # assign the QUAST script path
    quast_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_quast_code())

    # return the QUAST script path
    return quast_process_script

#-------------------------------------------------------------------------------

def get_quast_process_starter():
    '''
    Get the QUAST process starter path in the local computer.
    '''

    # assign the QUAST process starter path
    quast_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_quast_code())

    # return the QUAST starter path
    return quast_process_starter

#-------------------------------------------------------------------------------
    
def get_assembly_software_code_list():
    '''
    Get the code list of "assembly_software".
    '''

    return [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_ggtrinity_code(), xlib.get_cd_hit_est_code(),  xlib.get_transcript_filter_code()]

#-------------------------------------------------------------------------------
    
def get_assembly_software_code_list_text():
    '''
    Get the code list of "assembly_software" as text.
    '''

    return f'{xlib.get_soapdenovotrans_code()} ({xlib.get_soapdenovotrans_name()}) or {xlib.get_transabyss_code()} ({xlib.get_transabyss_name()}) or {xlib.get_trinity_code()} ({xlib.get_trinity_name()}) or {xlib.get_ggtrinity_code()} ({xlib.get_ggtrinity_name()}) or {xlib.get_cd_hit_est_code()} ({xlib.get_cd_hit_est_name()}) or {xlib.get_transcript_filter_code()} ({xlib.get_transcript_filter_name()})'

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the QUAST process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
