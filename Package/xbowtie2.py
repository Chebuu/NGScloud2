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
This file contains functions related to the Bowtie2 process used in both console
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

def create_bowtie2_config_file(experiment_id='exp001', reference_dataset_id='NONE', reference_file='NONE', assembly_dataset_id='sdnt-170101-235959', assembly_type='CONTIGS', read_dataset_id=xlib.get_uploaded_read_dataset_name(), read_type='PE', file_1_list=['rnaseq-a_1.fastq'], file_2_list=['rnaseq-a_2.fastq']):
    '''
    Create Bowtie2 config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # set the assembly software
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
    elif assembly_dataset_id.startswith(xlib.get_soapdenovo2_code()):
        assembly_software = xlib.get_soapdenovo2_code()
    elif assembly_dataset_id.startswith(xlib.get_starcode_code()):
        assembly_software = xlib.get_starcode_code()
    elif assembly_dataset_id.upper() == 'NONE':
        assembly_software = 'NONE'

    # create the Bowtie2 config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_bowtie2_config_file())):
            os.makedirs(os.path.dirname(get_bowtie2_config_file()))
        with open(get_bowtie2_config_file(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '# You must review the information of this file and update the values with the corresponding ones to the current run.\n')
            file_id.write( '#\n')
            file_id.write(f'# The reference file has to be located in the cluster directory {xlib.get_cluster_reference_dir()}/experiment_id/reference_dataset_id\n')
            file_id.write(f'# The assembly files have to be located in the cluster directory {xlib.get_cluster_result_dir()}/experiment_id/assembly_dataset_id\n')
            file_id.write(f'# The read files have to be located in the cluster directory {xlib.get_cluster_read_dir()}/experiment_id/read_dataset_id\n'.format(''.format()))
            file_id.write( '# The experiment_id, reference_dataset_id, reference_file, assembly_dataset_id and read_dataset_id are fixed in the identification section.\n')
            file_id.write( '#\n')
            file_id.write( '# You can consult the parameters of Bowtie2 and their meaning in "bowtie-bio.sourceforge.net/bowtie2/".\n')
            file_id.write( '#\n')
            file_id.write( '# In section "Bowtie2 parameters", the key "other_parameters" allows you to input additional parameters in the format:\n')
            file_id.write( '#\n')
            file_id.write( '#    other_parameters = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]\n')
            file_id.write( '#\n')
            file_id.write( '# parameter-i is a parameter name of Bowtie2 and value-i a valid value of parameter-i, e.g.\n')
            file_id.write( '#\n')
            file_id.write( '#    other_parameters = --reorder; --score-min=L,0,-0.2\n')
            file_id.write( '\n')
            file_id.write( '# This section has the information identifies the experiment.\n')
            file_id.write( '[identification]\n')
            file_id.write( '{0:<50} {1}\n'.format(f'experiment_id = {experiment_id}', '# experiment identification'))
            file_id.write( '{0:<50} {1}\n'.format(f'reference_dataset_id = {reference_dataset_id}', '# reference dataset identification or NONE if an assembly is used'))
            file_id.write( '{0:<50} {1}\n'.format(f'reference_file = {reference_file}', '# reference file name or NONE if an assembly is used'))
            file_id.write( '{0:<50} {1}\n'.format(f'assembly_software = {assembly_software}', f'# assembly software: {get_extended_assembly_software_code_list_text()}; or NONE if a reference is used'))
            file_id.write( '{0:<50} {1}\n'.format(f'assembly_dataset_id = {assembly_dataset_id}', '# assembly dataset identification or NONE if a reference is used'))
            file_id.write( '{0:<50} {1}\n'.format(f'assembly_type = {assembly_type}', f'# assembly type: CONTIGS or SCAFFOLDS in {xlib.get_soapdenovotrans_name()}; NONE in any other case'))
            file_id.write( '{0:<50} {1}\n'.format(f'read_dataset_id = {read_dataset_id}'.format(), '# read dataset identification'))
            file_id.write( '\n')
            file_id.write( '# This section has the information to set the Bowtie2 parameters\n')
            file_id.write( '[Bowtie2 parameters]\n')
            file_id.write( '{0:<50} {1}\n'.format( 'index_building = YES', f'# index building : {get_index_building_code_list_text()}'))
            file_id.write( '{0:<50} {1}\n'.format( 'large_index = YES', f'# a large index is force, even if the reference is less than ~ 4 billion nucleotides long: {get_large_index_code_list_text()}'))
            file_id.write( '{0:<50} {1}\n'.format( 'threads = 4', '# number of threads for use'))
            file_id.write( '{0:<50} {1}\n'.format( 'min_mp = 2', '# minimum mismatch penalty'))
            file_id.write( '{0:<50} {1}\n'.format( 'max_mp = 6', '# maximum mismatch penalty'))
            file_id.write( '{0:<50} {1}\n'.format( 'np = 1', '# penalty for positions where the read, reference, or both, contain an ambiguous character such as N'))
            file_id.write( '{0:<50} {1}\n'.format( 'open_rdg = 5', '# read gap open penalty'))
            file_id.write( '{0:<50} {1}\n'.format( 'extend_rdg = 3', '# read gap extend penalty'))
            file_id.write( '{0:<50} {1}\n'.format( 'open_rfg = 5', '# reference gap open penalty'))
            file_id.write( '{0:<50} {1}\n'.format( 'extend_rfg = 3', '# reference gap extend penalty'))
            file_id.write( '{0:<50} {1}\n'.format( 'orientation = FR', f'# orientation of paired-end reads: {get_orientation_code_list_text()}'))
            file_id.write( '{0:<50} {1}\n'.format( 'quality_score = 33', f'# FASTQ quality score: {get_quality_score_code_list_text()}'))
            file_id.write( '{0:<50} {1}\n'.format( 'other_parameters = NONE', '# additional parameters to the previous ones or NONE'))
            file_id.write( '\n')
            file_id.write( '# This section has the global information of all libraries.\n')
            file_id.write( '[library]\n')
            file_id.write( '{0:<50} {1}\n'.format( 'format = FASTQ', f'# format: {get_format_code_list_text()}'))
            file_id.write( '{0:<50} {1}\n'.format(f'read_type = {read_type}', f'# read type: {get_read_type_code_list_text()}'))
            file_id.write( '{0:<50} {1}\n'.format( 'library_concatenation = NO', f'# {get_library_concatenation_code_list_text()}'))
            for i in range(len(file_1_list)):
                file_id.write( '\n')
                if i == 0:
                    file_id.write( '# This section has the information of the first library.\n')
                file_id.write(f'[library-{i + 1}]\n')
                file_id.write( '{0:<50} {1}\n'.format(f'read_file_1 = {os.path.basename(file_1_list[i])}', '# name of the read file in SE read type or the + strand read file in PE case'))
                if read_type == 'SE':
                    file_id.write( '{0:<50} {1}\n'.format( 'read_file_2 = NONE', '# name of the - strand reads file in PE read type or NONE in SE case'))
                elif read_type == 'PE':
                    file_id.write( '{0:<50} {1}\n'.format(f'read_file_2 = {os.path.basename(file_2_list[i])}', '# name of the - strand reads file in PE read type or NONE in SE case'))
                if i == 0:
                    file_id.write( '\n')
                    file_id.write( '# If there are more libraries, you have to repeat the section library-1 with the data of each file.\n')
                    file_id.write( '# The section identification has to be library-n (n is an integer not repeated)\n')
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append(f'*** ERROR: The file {get_bowtie2_config_file()} can not be recreated')
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_bowtie2_process(cluster_name, log, function=None):
    '''
    Run a Bowtie2 process.
    '''

    # initialize the control variable
    OK = True

    # get the Bowtie2 option dictionary
    bowtie2_option_dict = xlib.get_option_dict(get_bowtie2_config_file())

    # get the experiment identification
    experiment_id = bowtie2_option_dict['identification']['experiment_id']

    # warn that the log window does not have to be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # check the Bowtie2 config file
    log.write(f'{xlib.get_separator()}\n')
    log.write(f'Checking the {xlib.get_bowtie2_name()} config file ...\n')
    (OK, error_list) = check_bowtie2_config_file(strict=True)
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

    # check the Bowtie2 is installed
    if OK:
        (OK, error_list, is_installed) = xbioinfoapp.is_installed_anaconda_package(xlib.get_bowtie2_anaconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_installed:
                log.write(f'*** ERROR: {xlib.get_bowtie2_name()} is not installed.\n')
                OK = False
        else:
            log.write(f'*** ERROR: The verification of {xlib.get_bowtie2_name()} installation could not be performed.\n')

    # check SAMtools is installed
    if OK:
        (OK, error_list, is_installed) = xbioinfoapp.is_installed_anaconda_package(xlib.get_samtools_anaconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_installed:
                log.write(f'*** ERROR: {xlib.get_samtools_name()} is not installed.\n')
                OK = False
        else:
            log.write(f'*** ERROR: The verification of {xlib.get_samtools_name()} installation could not be performed.\n')

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_bowtie2_code())
        command = f'mkdir --parents {current_run_dir}'
        (OK, _, _) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write(f'The directory path is {current_run_dir}.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Bowtie2 process script
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write(f'Building the process script {get_bowtie2_process_script()} ...\n')
        (OK, error_list) = build_bowtie2_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Bowtie2 process script in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write(f'Uploading the process script {get_bowtie2_process_script()} in the directory {current_run_dir} ...\n')
        cluster_path = f'{current_run_dir}/{os.path.basename(get_bowtie2_process_script())}'
        (OK, error_list) = xssh.put_file(sftp_client, get_bowtie2_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Bowtie2 process script in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write(f'Setting on the run permision of {current_run_dir}/{os.path.basename(get_bowtie2_process_script())} ...\n')
        command = f'chmod u+x {current_run_dir}/{os.path.basename(get_bowtie2_process_script())}'
        (OK, _, _) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Bowtie2 process starter
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write(f'Building the process starter {get_bowtie2_process_starter()} ...\n')
        (OK, error_list) = build_bowtie2_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Bowtie2 process starter in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write(f'Uploading the process starter {get_bowtie2_process_starter()} in the directory {current_run_dir} ...\n')
        cluster_path = f'{current_run_dir}/{os.path.basename(get_bowtie2_process_starter())}'
        (OK, error_list) = xssh.put_file(sftp_client, get_bowtie2_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Bowtie2 process starter in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write(f'Setting on the run permision of {current_run_dir}/{os.path.basename(get_bowtie2_process_starter())} ...\n')
        command = f'chmod u+x {current_run_dir}/{os.path.basename(get_bowtie2_process_starter())}'
        (OK, _, _) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # submit the Bowtie2 process
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write(f'Submitting the process script {current_run_dir}/{os.path.basename(get_bowtie2_process_starter())} ...\n')
        OK = xssh.submit_script(cluster_name, ssh_client, current_run_dir, os.path.basename(get_bowtie2_process_starter()), log)

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

def check_bowtie2_config_file(strict):
    '''
    Check the Bowtie2 config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        bowtie2_option_dict = xlib.get_option_dict(get_bowtie2_config_file())
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append('*** ERROR: The option dictionary could not be built from the config file')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in bowtie2_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = bowtie2_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "reference_dataset_id"
            reference_dataset_id = bowtie2_option_dict.get('identification', {}).get('reference_dataset_id', not_found)
            is_ok_reference_dataset_id = False
            if reference_dataset_id == not_found:
                error_list.append('*** ERROR: the key "reference_dataset_id" is not found in the section "identification".')
                OK = False
            else:
                is_ok_reference_dataset_id = True

            # check section "identification" - key "reference_file"
            reference_file = bowtie2_option_dict.get('identification', {}).get('reference_file', not_found)
            is_ok_reference_file = False
            if reference_file == not_found:
                error_list.append('*** ERROR: the key "reference_file" is not found in the section "identification".')
                OK = False
            else:
                is_ok_reference_file = True

            # check that "reference_file" has to be NONE if "reference_dataset_id" is NONE
            if is_ok_reference_dataset_id and is_ok_reference_file and reference_dataset_id.upper() == 'NONE' and reference_file.upper() != 'NONE':
                error_list.append('*** ERROR: "reference_file" has to be NONE if "reference_dataset_id" is NONE.')
                OK = False

            # check section "identification" - key "assembly_software"
            assembly_software = bowtie2_option_dict.get('identification', {}).get('assembly_software', not_found)
            is_ok_assembly_software = False
            if assembly_software == not_found:
                error_list.append('*** ERROR: the key "assembly_software" is not found in the section "identification".')
                OK = False
            elif assembly_software.upper() != 'NONE' and not xlib.check_code(assembly_software, get_extended_assembly_software_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "assembly_software" has to be {get_extended_assembly_software_code_list_text()}; or NONE if a reference is used.')
                OK = False
            else:
                is_ok_assembly_software = True

            # check that "assembly_software" has to be NONE if "reference_dataset_id" is not NONE, and vice versa
            if is_ok_reference_dataset_id and is_ok_assembly_software and (reference_dataset_id.upper() == 'NONE' and assembly_software.upper() == 'NONE' or reference_dataset_id.upper() != 'NONE' and assembly_software.upper() != 'NONE'):
                error_list.append('*** ERROR: "assembly_software" has to be NONE if "reference_dataset_id" is not NONE, and vice versa.')
                OK = False

            # check section "identification" - key "assembly_dataset_id"
            assembly_dataset_id = bowtie2_option_dict.get('identification', {}).get('assembly_dataset_id', not_found)
            is_ok_assembly_dataset_id = False
            if assembly_dataset_id == not_found:
                error_list.append('*** ERROR: the key "assembly_dataset_id" is not found in the section "identification".')
                OK = False
            elif assembly_dataset_id.upper() != 'NONE' and not xlib.check_startswith(assembly_dataset_id, get_extended_assembly_software_code_list(), case_sensitive=True):
                error_list.append(f'*** ERROR: the key "assembly_dataset_id" does not have to start with {get_extended_assembly_software_code_list_text()}.')
                OK = False
            else:
                is_ok_assembly_dataset_id = True

            # check that "assembly_dataset_id" has to be NONE if "assembly_software" is NONE
            if is_ok_assembly_software and is_ok_assembly_dataset_id and assembly_software.upper() == 'NONE' and assembly_dataset_id.upper() != 'NONE':
                error_list.append('*** ERROR: "assembly_dataset_id" has to be NONE if "assembly_software" is NONE.')
                OK = False

            # check section "identification" - key "assembly_type"
            assembly_type = bowtie2_option_dict.get('identification', {}).get('assembly_type', not_found)
            if assembly_type == not_found:
                error_list.append('*** ERROR: the key "assembly_type" is not found in the section "identification".')
                OK = False
            elif (assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()) or assembly_dataset_id.startswith(xlib.get_soapdenovo2_code())) and assembly_type.upper() not in ['CONTIGS', 'SCAFFOLDS'] or \
                not (assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()) or assembly_dataset_id.startswith(xlib.get_soapdenovo2_code())) and assembly_type.upper() != 'NONE':
                    error_list.append(f'*** ERROR: the key "assembly_type" has to be CONTIGS or SCAFFOLDS in {xlib.get_soapdenovotrans_name()} and {xlib.get_soapdenovo2_name()}; or NONE in any other case.')
                    OK = False

            # check section "identification" - key "read_dataset_id"
            read_dataset_id = bowtie2_option_dict.get('identification', {}).get('read_dataset_id', not_found)
            if read_dataset_id == not_found:
                error_list.append('*** ERROR: the key "read_dataset_id" is not found in the section "identification".')
                OK = False

        # check section "Bowtie2 parameters"
        if 'Bowtie2 parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Bowtie2 parameters" is not found.')
            OK = False
        else:

            # check section "Bowtie2 parameters" - key "index_building"
            index_building = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('index_building', not_found)
            if index_building == not_found:
                error_list.append('*** ERROR: the key "index_building" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_code(index_building, get_index_building_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "index_building" has to be {get_index_building_code_list_text()}.')
                OK = False

            # check section "Bowtie2 parameters" - key "large_index"
            large_index = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('large_index', not_found)
            if large_index == not_found:
                error_list.append('*** ERROR: the key "large_index" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_code(large_index, get_large_index_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "large_index" has to be {get_large_index_code_list_text()}.')
                OK = False

            # check section "Bowtie2 parameters" - key "threads"
            threads = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('threads', not_found)
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_int(threads, minimum=1):
                error_list.append('*** ERROR: the key "threads" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Bowtie2 parameters" - key "min_mp"
            min_mp = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('min_mp', not_found)
            is_ok_min_mp = False
            if min_mp == not_found:
                error_list.append('*** ERROR: the key "min_mp" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_int(min_mp, minimum=0):
                error_list.append('*** ERROR: the key "min_mp" has to be an integer number greater than or equal to 0.')
                OK = False
            else:
                is_ok_min_mp = True


            # check section "Bowtie2 parameters" - key "max_mp"
            max_mp = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('max_mp', not_found)
            is_ok_max_mp = False
            if max_mp == not_found:
                error_list.append('*** ERROR: the key "max_mp" is not found in the section "Bowtie2 parameters".')
                OK = False
                max_mp = 99999999999999
            elif not xlib.check_int(max_mp, minimum=0):
                error_list.append('*** ERROR: the key "max_mp" has to be an integer number greater than or equal to 0.')
                OK = False
            else:
                is_ok_max_mp = True

            # check if max_mp value is greater than or equal than min_mp value
            if is_ok_min_mp and is_ok_max_mp and int(max_mp) < int(min_mp):
                error_list.append(f'*** ERROR: The value max_mp value ({max_mp}) is less than the min_mp value ({min_mp}).')
                OK = False

            # check section "Bowtie2 parameters" - key "np"
            np = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('np', not_found)
            if np == not_found:
                error_list.append('*** ERROR: the key "np" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_int(np, minimum=0):
                error_list.append('*** ERROR: the key "np" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Bowtie2 parameters" - key "open_rdg"
            open_rdg = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('open_rdg', not_found)
            if open_rdg == not_found:
                error_list.append('*** ERROR: the key "open_rdg" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_int(open_rdg, minimum=0):
                error_list.append('*** ERROR: the key "open_rdg" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Bowtie2 parameters" - key "extend_rdg"
            extend_rdg = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('extend_rdg', not_found)
            if extend_rdg == not_found:
                error_list.append('*** ERROR: the key "extend_rdg" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_int(extend_rdg, minimum=0):
                error_list.append('*** ERROR: the key "extend_rdg" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Bowtie2 parameters" - key "open_rfg"
            open_rfg = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('open_rfg', not_found)
            if open_rfg == not_found:
                error_list.append('*** ERROR: the key "open_rfg" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_int(open_rfg, minimum=0):
                error_list.append('*** ERROR: the key "open_rfg" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Bowtie2 parameters" - key "extend_rfg"
            extend_rfg = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('extend_rfg', not_found)
            if extend_rfg == not_found:
                error_list.append('*** ERROR: the key "extend_rfg" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_int(extend_rfg, minimum=0):
                error_list.append('*** ERROR: the key "extend_rfg" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Bowtie2 parameters" - key "orientation"
            orientation = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('orientation', not_found)
            if orientation == not_found:
                error_list.append('*** ERROR: the key "orientation" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif not xlib.check_code(orientation, get_orientation_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "orientation" has to be {get_orientation_code_list_text()}.')
                OK = False

            # check section "Bowtie2 parameters" - key "quality_score"
            quality_score = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('quality_score', not_found)
            if quality_score == not_found:
                error_list.append('*** ERROR: the key "quality_score" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif quality_score not in get_quality_score_code_list():
                error_list.append(f'*** ERROR: the key "quality_score" has to be {get_quality_score_code_list_text()}.')
                OK = False

            # check section "Bowtie2 parameters" - key "other_parameters"
            not_allowed_parameters_list = ['threads', 'qseq', 'phred33', 'phred64', 'mp', 'np', 'rdg', 'rfg', 'time', 'un', 'un-gz', 'un-bz2', 'un-lz4', 'al', 'al-gz', 'al-bz2', 'un-conc', 'un-conc-gz', 'un-conc-bz2', 'un-conc-lz4', 'al-conc', 'al-conc-gz', 'al-conc-bz2', 'al-conc-lz4', '--no-unal', 'quiet', 'met-file']
            other_parameters = bowtie2_option_dict.get('Bowtie2 parameters', {}).get('other_parameters', not_found)
            if other_parameters == not_found:
                error_list.append('*** ERROR: the key "other_parameters" is not found in the section "Bowtie2 parameters".')
                OK = False
            elif other_parameters.upper() != 'NONE':
                (OK, error_list2) = xlib.check_parameter_list(other_parameters, "other_parameters", not_allowed_parameters_list)
                error_list = error_list + error_list2

        # check section "library"
        if 'library' not in sections_list:
            error_list.append('*** ERROR: the section "library" is not found.')
            OK = False
        else:

            # check section "library" - key "format"
            format = bowtie2_option_dict.get('library', {}).get('format', not_found)
            if format == not_found:
                error_list.append('*** ERROR: the key "format" is not found in the section "library".')
                OK = False
            elif not xlib.check_code(format, get_format_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "format" has to be {get_format_code_list_text()}.')
                OK = False

            # check section "library" - key "read_type"
            read_type = bowtie2_option_dict.get('library', {}).get('read_type', not_found)
            if read_type == not_found:
                error_list.append('*** ERROR: the key "read_type" is not found in the section "library".')
                OK = False
            elif not xlib.check_code(read_type, get_read_type_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "read_type" has to be {get_read_type_code_list_text()}.')
                OK = False

            # check section "library" - key "library_concatenation"
            library_concatenation = bowtie2_option_dict.get('library', {}).get('library_concatenation', not_found)
            if library_concatenation == not_found:
                error_list.append('*** ERROR: the key "library_concatenation" is not found in the section "library".')
                OK = False
            elif not xlib.check_code(library_concatenation, get_library_concatenation_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "library_concatenation" has to be {get_library_concatenation_code_list_text()}.')
                OK = False

        # check section "library-1"
        if 'library-1' not in sections_list:
            error_list.append('*** ERROR: the section "library-1" is not found.')
            OK = False

        # check all sections "library-n"
        for section in sections_list:

            if section not in ['identification', 'Bowtie2 parameters', 'library']:

                # check than the section identification is like library-n 
                if not re.match('^library-[0-9]+$', section):
                    error_list.append(f'*** ERROR: the section "{section}" has a wrong identification.')
                    OK = False

                else:

                    # check section "library-n" - key "read_file_1"
                    read_file_1 = bowtie2_option_dict.get(section, {}).get('read_file_1', not_found)
                    if read_file_1 == not_found:
                        error_list.append(f'*** ERROR: the key "read_file_1" is not found in the section "{section}"')
                        OK = False

                    # check section "library-n" - key "read_file_2"
                    read_file_2 = bowtie2_option_dict.get(section, {}).get('read_file_2', not_found)
                    if read_file_2 == not_found:
                        error_list.append(f'*** ERROR: the key "read_file_2" is not found in the section "{section}"')
                        OK = False

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append(f'\nThe {xlib.get_bowtie2_name()} config file is not valid. Please, correct this file or recreate it.')

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_bowtie2_process_script(cluster_name, current_run_dir):
    '''
    Build the current Bowtie2 process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the Bowtie2 option dictionary
    bowtie2_option_dict = xlib.get_option_dict(get_bowtie2_config_file())

    # get the options
    experiment_id = bowtie2_option_dict['identification']['experiment_id']
    reference_dataset_id = bowtie2_option_dict['identification']['reference_dataset_id']
    reference_file = bowtie2_option_dict['identification']['reference_file']
    assembly_software = bowtie2_option_dict['identification']['assembly_software']
    assembly_dataset_id = bowtie2_option_dict['identification']['assembly_dataset_id']
    assembly_type = bowtie2_option_dict['identification']['assembly_type']
    read_dataset_id = bowtie2_option_dict['identification']['read_dataset_id']
    index_building = bowtie2_option_dict['Bowtie2 parameters']['index_building']
    large_index = bowtie2_option_dict['Bowtie2 parameters']['large_index']
    threads = bowtie2_option_dict['Bowtie2 parameters']['threads']
    min_mp = bowtie2_option_dict['Bowtie2 parameters']['min_mp']
    max_mp = bowtie2_option_dict['Bowtie2 parameters']['max_mp']
    np = bowtie2_option_dict['Bowtie2 parameters']['np']
    open_rdg = bowtie2_option_dict['Bowtie2 parameters']['open_rdg']
    extend_rdg = bowtie2_option_dict['Bowtie2 parameters']['extend_rdg']
    open_rfg = bowtie2_option_dict['Bowtie2 parameters']['open_rfg']
    extend_rfg = bowtie2_option_dict['Bowtie2 parameters']['extend_rfg']
    orientation = bowtie2_option_dict['Bowtie2 parameters']['orientation']
    quality_score = bowtie2_option_dict['Bowtie2 parameters']['quality_score']
    other_parameters = bowtie2_option_dict['Bowtie2 parameters']['other_parameters']
    format = bowtie2_option_dict['library']['format']
    read_type = bowtie2_option_dict['library']['read_type']
    library_concatenation = bowtie2_option_dict['library']['library_concatenation']

    # get the sections list
    sections_list = []
    for section in bowtie2_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build read file lists
    read_file_1_list = []
    read_file_2_list = []
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^library-[0-9]+$', section):
            read_file_1 = bowtie2_option_dict[section]['read_file_1']
            read_file_1 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_1)
            read_file_1_list.append(read_file_1)
            if read_type.upper() == 'PE':
                read_file_2 = bowtie2_option_dict[section]['read_file_2']
                read_file_2 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_2)
                read_file_2_list.append(read_file_2)
    if library_concatenation.upper() == 'YES':
        read_file_1_list = [",".join(read_file_1_list)]
        if read_type.upper() == 'PE':
            read_file_2_list = [",".join(read_file_2_list)]

    # set the cluster reference dataset directory
    if reference_dataset_id.upper() != 'NONE':
        cluster_reference_dataset_dir = xlib.get_cluster_reference_dataset_dir(reference_dataset_id)
    else:
        # -- cluster_reference_dataset_dir = xlib.get_cluster_reference_dataset_dir('asemblies')
        cluster_reference_dataset_dir = xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)

    # set the cluster reference file
    if reference_dataset_id.upper() != 'NONE':
        cluster_reference_file = xlib.get_cluster_reference_file(reference_dataset_id, reference_file)
    else:
        if assembly_software in [xlib.get_soapdenovotrans_code(), xlib.get_soapdenovo2_code()]:
            if assembly_type == 'CONTIGS':
                cluster_reference_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/{experiment_id}-{assembly_dataset_id}.contig'
            elif  assembly_type == 'SCAFFOLDS':
                cluster_reference_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/{experiment_id}-{assembly_dataset_id}.scafSeq'
        elif assembly_software == xlib.get_transabyss_code():
            cluster_reference_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/transabyss-final.fa'
        elif assembly_software == xlib.get_trinity_code():
            cluster_reference_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/Trinity.fasta'
        elif assembly_software == xlib.get_ggtrinity_code():
            cluster_reference_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/Trinity-GG.fasta'
        elif assembly_software == xlib.get_cd_hit_est_code():
            cluster_reference_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/clustered-transcriptome.fasta'
        elif assembly_software == xlib.get_transcript_filter_code():
            cluster_reference_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/filtered-transcriptome.fasta'
        elif assembly_software == xlib.get_starcode_code():
            cluster_reference_file = f'{xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id)}/starcode.fasta'

    # set the directory and basename of the index Bowtie2
    if reference_dataset_id.upper() != 'NONE':
        (reference_file_name, _) = os.path.splitext(reference_file)
        bowtie2_index_dir = f'{cluster_reference_dataset_dir}/{reference_file_name}-bowtie2_indexes'
    else:
        bowtie2_index_dir = f'{cluster_reference_dataset_dir}/{assembly_dataset_id}-bowtie2_indexes'
    bowtie2_index_basename = 'bowtie2_indexes'

    # set the alignment file
    alignment_file = 'alignment.sam'

    # set the file of unpaired reads that fail to align
    un_gz = 'unpairednotaligned.fastq.gz'

    # set the file of unpaired reads that align at least once
    al_gz = 'unpairedaligned.fastq.gz'

    # set the file of paired-end reads that fail to align concordantly
    un_conc_gz = 'pairednotaligned.fastq.gz'

    # set the file of paired-end reads that align concordantly at least once
    al_conc_gz = 'pairednotaligned.fastq.gz'

    # set the metric file
    metric_file = 'metrics.txt'

    # write the GSMAP process script
    try:
        if not os.path.exists(os.path.dirname(get_bowtie2_process_script())):
            os.makedirs(os.path.dirname(get_bowtie2_process_script()))
        with open(get_bowtie2_process_script(), mode='w', encoding='iso-8859-1', newline='\n') as script_file_id:
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
            script_file_id.write(f'CURRENT_DIR={current_run_dir}\n')
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
            script_file_id.write( 'function print_bowtie2_version\n')
            script_file_id.write( '{\n')
            script_file_id.write(f'    source activate {xlib.get_bowtie2_anaconda_code()}\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    bowtie2 --version\n')
            script_file_id.write( '    conda deactivate\n')
            script_file_id.write( '}\n')
            if index_building.upper() == 'YES':
                script_file_id.write( '#-------------------------------------------------------------------------------\n')
                script_file_id.write( 'function build_bowtie2_indexes\n')
                script_file_id.write( '{\n')
                script_file_id.write(f'    source activate {xlib.get_bowtie2_anaconda_code()}\n')
                script_file_id.write( '    cd $CURRENT_DIR\n')
                script_file_id.write( '    echo "$SEP"\n')
                script_file_id.write( '    echo "Building indexes ..."\n')
                script_file_id.write( '    /usr/bin/time \\\n')
                script_file_id.write(f'        --format="{xlib.get_time_output_format(separator=False)}" \\\n')
                script_file_id.write( '        bowtie2-build \\\n')
                script_file_id.write(f'            --threads {threads} \\\n')
                if large_index.upper() == 'YES':
                    script_file_id.write( '            --large-index \\\n')
                script_file_id.write( '            -f \\\n')
                script_file_id.write(f'            {cluster_reference_file} \\\n')
                script_file_id.write(f'            {bowtie2_index_basename}\n')
                script_file_id.write( '    RC=$?\n')
                script_file_id.write( '    if [ $RC -ne 0 ]; then manage_error bowtie2-build $RC; fi\n')
                script_file_id.write(f'    mkdir --parents {bowtie2_index_dir}\n')
                script_file_id.write( '    RC=$?\n')
                script_file_id.write( '    if [ $RC -ne 0 ]; then manage_error mkdir $RC; fi\n')
                script_file_id.write(f'    mv -f {bowtie2_index_basename}.* {bowtie2_index_dir}\n')
                script_file_id.write( '    RC=$?\n')
                script_file_id.write( '    if [ $RC -ne 0 ]; then manage_error mv $RC; fi\n')
                script_file_id.write( '    echo "Indexes are built."\n')
                script_file_id.write( '    conda deactivate\n')
                script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function run_bowtie2_process\n')
            script_file_id.write( '{\n')
            script_file_id.write(f'    source activate {xlib.get_bowtie2_anaconda_code()}\n')
            script_file_id.write( '    cd $CURRENT_DIR\n')
            for i in range(len(read_file_1_list)):
                # set file names for the library
                if library_concatenation.upper() == 'YES':
                    library_name = 'concatenated_libraries'
                    alignment_file = 'alignment.sam'
                    un_gz = 'unpairednotaligned.fastq.gz'
                    al_gz = 'unpairedaligned.fastq.gz'
                    un_conc_gz = 'pairednotaligned.fastq.gz'
                    al_conc_gz = 'pairednotaligned.fastq.gz'
                    metric_file = 'metrics.txt'
                else:
                    if read_file_1.endswith('.gz'):
                        (library_name, _) = os.path.splitext(os.path.basename(read_file_1_list[i][:-3]))
                    else:
                        (library_name, _) = os.path.splitext(os.path.basename(read_file_1_list[i]))
                    alignment_file = f'{library_name}-alignment.sam'
                    un_gz = f'{library_name}-unpairednotaligned.fastq.gz'
                    al_gz = f'{library_name}-unpairedaligned.fastq.gz'
                    un_conc_gz = f'{library_name}-pairednotaligned.fastq.gz'
                    al_conc_gz = f'{library_name}-pairednotaligned.fastq.gz'
                    metric_file = f'{library_name}-metrics.txt'
                # write the instructions for the library
                script_file_id.write( '    echo "$SEP"\n')
                script_file_id.write(f'    echo "Mapping reads of {library_name} ..."\n')
                script_file_id.write( '    /usr/bin/time \\\n')
                script_file_id.write(f'        --format="{xlib.get_time_output_format(separator=False)}" \\\n')
                script_file_id.write( '        bowtie2 \\\n')
                script_file_id.write(f'            --threads {threads} \\\n')
                script_file_id.write( '            --mm \\\n')
                script_file_id.write(f'            --mp {max_mp},{min_mp} \\\n')
                script_file_id.write(f'            --np {np} \\\n')
                script_file_id.write(f'            --rdg {open_rdg},{extend_rdg} \\\n')
                script_file_id.write(f'            --rfg {open_rfg},{extend_rfg} \\\n')
                script_file_id.write(f'            --{orientation.lower()} \\\n')
                if quality_score == '33':
                    script_file_id.write( '            --phred33 \\\n')
                elif quality_score == '64':
                    script_file_id.write( '            --phred64 \\\n')
                if other_parameters.upper() != 'NONE':
                    parameter_list = [x.strip() for x in other_parameters.split(';')]
                    for i in range(len(parameter_list)):
                        if parameter_list[i].find('=') > 0:
                            pattern = r'^--(.+)=(.+)$'
                            mo = re.search(pattern, parameter_list[i])
                            parameter_name = mo.group(1).strip()
                            parameter_value = mo.group(2).strip()
                            script_file_id.write(f'            --{parameter_name} {parameter_value} \\\n')
                        else:
                            pattern = r'^--(.+)$'
                            mo = re.search(pattern, parameter_list[i])
                            parameter_name = mo.group(1).strip()
                            script_file_id.write(f'            --{parameter_name} \\\n')
                script_file_id.write(f'            -x {bowtie2_index_dir}/{bowtie2_index_basename} \\\n')
                if format.upper() == 'FASTQ':
                    script_file_id.write( '            -q \\\n')
                elif format.upper() == 'FASTA':
                    script_file_id.write( '            -f \\\n')
                if read_type.upper() == 'SE':
                    script_file_id.write(f'            -U {",".join(read_file_1_list)} \\\n')
                elif read_type.upper() == 'PE':
                    script_file_id.write(f'            -1 {",".join(read_file_1_list)} \\\n')
                    script_file_id.write(f'            -2 {",".join(read_file_2_list)} \\\n')
                script_file_id.write( '            --no-unal \\\n')
                script_file_id.write(f'            -S {alignment_file} \\\n')
                script_file_id.write(f'            --un-gz {un_gz} \\\n')
                script_file_id.write(f'            --al-gz {al_gz} \\\n')
                script_file_id.write(f'            --un-conc-gz {un_conc_gz} \\\n')
                script_file_id.write(f'            --al-conc-gz {al_conc_gz} \\\n')
                script_file_id.write(f'            --met-file {metric_file} \\\n')
                script_file_id.write( '            --time\n')
                script_file_id.write( '    RC=$?\n')
                script_file_id.write( '    if [ $RC -ne 0 ]; then manage_error bowtie2 $RC; fi\n')
                script_file_id.write( '    echo "Reads are mapped."\n')
            script_file_id.write( '    conda deactivate\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function convert_sam2bam\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    cd $CURRENT_DIR\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "Converting SAM files to BAM format ..."\n')
            script_file_id.write(f'    source activate {xlib.get_samtools_anaconda_code()}\n')
            script_file_id.write( '    ls *.sam > sam-files.txt\n')
            script_file_id.write( '    while read FILE_SAM; do\n')
            script_file_id.write( '        FILE_BAM=`basename $FILE_SAM | sed "s|.sam|.bam|g"`\n')
            script_file_id.write( '        echo "Converting file $FILE_SAM to BAM format ..."\n')
            script_file_id.write(f'        samtools view --threads {threads} -b -S -o $FILE_BAM $FILE_SAM\n')
            script_file_id.write( '        RC=$?\n')
            script_file_id.write( '        if [ $RC -ne 0 ]; then manage_error samtools-view $RC; fi\n')
            script_file_id.write( '        echo "$FILE_BAM is created."\n')
            script_file_id.write( '        echo "Compressing $FILE_SAM ..."\n')
            script_file_id.write( '        gzip $FILE_SAM\n')
            script_file_id.write( '        RC=$?\n')
            script_file_id.write( '        if [ $RC -ne 0 ]; then manage_error gzip $RC; fi\n')
            script_file_id.write( '        echo "$FILE_SAM is compressed."\n')
            script_file_id.write( '    done < sam-files.txt\n')
            script_file_id.write( '    conda deactivate\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function sort_and_index_bam_files\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    cd $CURRENT_DIR\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write(f'    source activate {xlib.get_samtools_anaconda_code()}\n')
            script_file_id.write( '    ls *.bam > bam-files.txt\n')
            script_file_id.write( '    while read FILE_BAM; do\n')
            script_file_id.write( '        FILE_SORTED_BAM=`basename $FILE_BAM | sed "s|.bam|.sorted.bam|g"`\n')
            script_file_id.write( '        echo "Sorting and indexing $FILE_BAM ..."\n')
            script_file_id.write(f'        samtools sort --threads {threads} $FILE_BAM -o $FILE_SORTED_BAM\n')
            script_file_id.write( '        RC=$?\n')
            script_file_id.write( '        if [ $RC -ne 0 ]; then manage_error samtools-sort $RC; fi\n')
            script_file_id.write(f'        samtools index -@ {threads} $FILE_SORTED_BAM\n')
            script_file_id.write( '        RC=$?\n')
            script_file_id.write( '        if [ $RC -ne 0 ]; then manage_error samtools-index $RC; fi\n')
            script_file_id.write( '        echo "$FILE_SORTED_BAM is created."\n')
            script_file_id.write( '        echo "Deleting file $FILE_BAM ..."\n')
            script_file_id.write( '        rm -f $FILE_BAM\n')
            script_file_id.write( '        RC=$?\n')
            script_file_id.write( '        if [ $RC -ne 0 ]; then manage_error rm $RC; fi\n')
            script_file_id.write( '        echo "$FILE_BAM is deleted."\n')
            script_file_id.write( '    done < bam-files.txt\n')
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
            process_name = f'{xlib.get_bowtie2_name()} process'
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
            script_file_id.write( 'print_bowtie2_version\n')
            if index_building.upper() == 'YES':
                script_file_id.write( 'build_bowtie2_indexes\n')
            script_file_id.write( 'run_bowtie2_process\n')
            script_file_id.write( 'convert_sam2bam\n')
            script_file_id.write( 'sort_and_index_bam_files\n')
            script_file_id.write( 'end\n')
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append(f'*** ERROR: The file {get_bowtie2_process_script()} can not be created')
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_bowtie2_process_starter(current_run_dir):
    '''
    Build the starter of the current Bowtie2 process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Bowtie2 process starter
    try:
        if not os.path.exists(os.path.dirname(get_bowtie2_process_starter())):
            os.makedirs(os.path.dirname(get_bowtie2_process_starter()))
        with open(get_bowtie2_process_starter(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '#!/bin/bash\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write(f'{current_run_dir}/{os.path.basename(get_bowtie2_process_script())} &>>{current_run_dir}/{xlib.get_cluster_log_file()}\n')
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append(f'*** ERROR: The file {get_bowtie2_process_starter()} can not be created')
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_bowtie2_config_file():
    '''
    Get the Bowtie2 config file path.
    '''

    # assign the Bowtie2 config file path
    bowtie2_config_file = f'{xlib.get_config_dir()}/{xlib.get_bowtie2_code()}-config.txt'

    # return the Bowtie2 config file path
    return bowtie2_config_file

#-------------------------------------------------------------------------------

def get_bowtie2_process_script():
    '''
    Get the Bowtie2 process script path in the local computer.
    '''

    # assign the Bowtie2 script path
    bowtie2_process_script = f'{xlib.get_temp_dir()}/{xlib.get_bowtie2_code()}-process.sh'

    # return the Bowtie2 script path
    return bowtie2_process_script

#-------------------------------------------------------------------------------

def get_bowtie2_process_starter():
    '''
    Get the Bowtie2 process starter path in the local computer.
    '''

    # assign the Bowtie2 process starter path
    bowtie2_process_starter = f'{xlib.get_temp_dir()}/{xlib.get_bowtie2_code()}-process-starter.sh'

    # return the Bowtie2 starter path
    return bowtie2_process_starter

#-------------------------------------------------------------------------------

def get_extended_assembly_software_code_list():
    '''
    Get the code list of "assembly_software".
    '''

    return [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_ggtrinity_code(), xlib.get_cd_hit_est_code(),  xlib.get_transcript_filter_code(), xlib.get_soapdenovo2_code(), xlib.get_starcode_name()]

#-------------------------------------------------------------------------------

def get_extended_assembly_software_code_list_text():
    '''
    Get the code list of "assembly_software" as text.
    '''

    return f'{xlib.get_soapdenovotrans_code()} ({xlib.get_soapdenovotrans_name()}) or {xlib.get_transabyss_code()} ({xlib.get_transabyss_name()}) or {xlib.get_trinity_code()} ({xlib.get_trinity_name()}) or {xlib.get_ggtrinity_code()} ({xlib.get_ggtrinity_name()}) or {xlib.get_cd_hit_est_code()} ({xlib.get_cd_hit_est_name()}) or {xlib.get_transcript_filter_code()} ({xlib.get_transcript_filter_name()}) or {xlib.get_soapdenovo2_code()} ({xlib.get_soapdenovo2_name()}) or {xlib.get_starcode_code()} ({xlib.get_starcode_name()})'

#-------------------------------------------------------------------------------

def get_index_building_code_list():
    '''
    Get the code list of "index_building".
    '''

    return ['YES', 'NO']

#-------------------------------------------------------------------------------

def get_index_building_code_list_text():
    '''
    Get the code list of "index_building" as text.
    '''

    return 'YES (built indexes) or NO (old indexes will be used)'

#-------------------------------------------------------------------------------

def get_large_index_code_list():
    '''
    Get the code list of "large_index".
    '''

    return ['YES', 'NO']

#-------------------------------------------------------------------------------

def get_large_index_code_list_text():
    '''
    Get the code list of "large_index" as text.
    '''

    return str(get_large_index_code_list()).strip('[]').replace('\'','').replace(',', ' or')

#-------------------------------------------------------------------------------

def get_orientation_code_list():
    '''
    Get the code list of "orientation".
    '''

    return ['FR', 'RF', 'FF']

#-------------------------------------------------------------------------------

def get_orientation_code_list_text():
    '''
    Get the code list of "orientation" as text.
    '''

    return 'FR (fwd-rev, or typical Illumina) or RF (rev-fwd, for circularized inserts) or FF (fwd-fwd, same strand)'

#-------------------------------------------------------------------------------

def get_quality_score_code_list():
    '''
    Get the code list of "quality_score".
    '''

    return ['33', '64']

#-------------------------------------------------------------------------------

def get_quality_score_code_list_text():
    '''
    Get the code list of "quality_score" as text.
    '''

    return '33 (Phred+33) or 64 (Phred+64)'

#-------------------------------------------------------------------------------

def get_format_code_list():
    '''
    Get the code list of "format".
    '''

    return ['FASTA', 'FASTQ']

#-------------------------------------------------------------------------------

def get_format_code_list_text():
    '''
    Get the code list of "format" as text.
    '''

    return str(get_format_code_list()).strip('[]').replace('\'','').replace(',', ' or')

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

def get_library_concatenation_code_list():
    '''
    Get the code list of "library_concatenation".
    '''

    return ['YES', 'NO']

#-------------------------------------------------------------------------------

def get_library_concatenation_code_list_text():
    '''
    Get the code list of "library_concatenation" as text.
    '''

    return 'YES (map concatanated libraries) or NO (map each library separately)'

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the Bowtie2 process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
