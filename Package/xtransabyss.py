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
This file contains functions related to the Trans-ABySS process used in both
console mode and gui mode.
'''

#-------------------------------------------------------------------------------

import os
import re
import subprocess
import sys

import xbioinfoapp
import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def create_transabyss_config_file(experiment_id='exp001', read_dataset_id=xlib.get_uploaded_read_dataset_name(), read_type='PE', file_1_list=['rnaseq-a_1.fastq'], file_2_list=['rnaseq-a_2.fastq']):
    '''
    Create Trans-ABySS config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # create the Trans-ABySS config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_transabyss_config_file())):
            os.makedirs(os.path.dirname(get_transabyss_config_file()))
        with open(get_transabyss_config_file(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '# You must review the information of this file and update the values with the corresponding ones to the current run.\n')
            file_id.write( '#\n')
            file_id.write(f'# The read files have to be located in the cluster directory {xlib.get_cluster_read_dir()}/experiment_id/read_dataset_id\n')
            file_id.write( '{0}\n'.format('# The experiment_id and read_dataset_id names are fixed in the identification section.'))
            file_id.write( '#\n')
            file_id.write( '{0}\n'.format('# You can consult the parameters of Trans-ABySS and their meaning in "http://www.bcgsc.ca/platform/bioinfo/software/trans-abyss2.'))
            file_id.write( '#\n')
            file_id.write( '{0}\n'.format('# There are two formats to set an option:'))
            file_id.write( '#\n')
            file_id.write( '{0}\n'.format('#    option = value                             <- if the option supports a single value'))
            file_id.write( '#\n')
            file_id.write( '{0}\n'.format('#    option = value-1, value-2, ..., value-n    <- if the option supports a values list'))
            file_id.write( '#\n')
            file_id.write( '{0}\n'.format('# In section "Trans-ABySS parameters", the key "other_parameters" allows you to input additional parameters in the format:'))
            file_id.write( '#\n')
            file_id.write( '#    other_parameters = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]\n')
            file_id.write( '#\n')
            file_id.write( '{0}\n'.format('# parameter-i is a parameter name of Trans-ABySS and value-i a valid value of parameter-i, e.g.'))
            file_id.write( '#\n')
            file_id.write( '{0}\n'.format('#    other_parameters = --qends=4; --noref)'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information that identifies the experiment.'))
            file_id.write( '[identification]\n')
            file_id.write( '{0:<50} {1}\n'.format(f'experiment_id = {experiment_id}', '# experiment identification'))
            file_id.write( '{0:<50} {1}\n'.format(f'read_dataset_id = {read_dataset_id}', '# read dataset identification'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information to set the Trans-ABySS parameters'))
            file_id.write( '{0}\n'.format('[Trans-ABySS parameters]'))
            file_id.write( '{0:<50} {1}\n'.format('threads = 4', '# number of threads for use'))
            file_id.write( '{0:<50} {1}\n'.format('length = 100', '# minimum output sequence length'))
            file_id.write( '{0:<50} {1}\n'.format('kmer = 32', '# value or values list of k-mer size'))
            file_id.write( '{0:<50} {1}\n'.format('cov = 2', '# minimum mean k-mer coverage of a unitig'))
            file_id.write( '{0:<50} {1}\n'.format('eros = 2', '# minimum erosion k-mer coverage'))
            file_id.write( '{0:<50} {1}\n'.format('seros = 0', '# minimum erosion k-mer coverage per strand'))
            file_id.write( '{0:<50} {1}\n'.format('gsim = 2', '# maximum iterations of graph simplification'))
            file_id.write( '{0:<50} {1}\n'.format('indel = 1', '# indel size tolerance'))
            file_id.write( '{0:<50} {1}\n'.format('island = 0', '# minimum length of island unitigs'))
            file_id.write( '{0:<50} {1}\n'.format('useblat = NO', '# use BLAT alignments to remove redundant sequences: {0}'.format(get_useblat_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('pid = 0.95', '# minimum percent sequence identity of redundant sequences'))
            file_id.write( '{0:<50} {1}\n'.format('walk = 0.05', '# percentage of mean k-mer coverage of seed for path-walking'))
            file_id.write( '{0:<50} {1}\n'.format('cleanup = 1', '# level of clean-up of intermediate files: {0}'.format(get_cleanup_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format( 'other_parameters = NONE', '# additional parameters to the previous ones or NONE'))
            file_id.write( '\n')
            file_id.write( '# This section has the global information of all libraries.\n')
            file_id.write( '[library]\n')
            file_id.write( '{0:<50} {1}\n'.format( 'format = FASTQ', f'# format: {get_format_code_list_text()}'))
            file_id.write( '{0:<50} {1}\n'.format(f'read_type = {read_type}', f'# read type: {get_read_type_code_list_text()}'))
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
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transabyss_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_transabyss_process(cluster_name, log, function=None):
    '''
    Run an experiment corresponding to the options in Trans-ABySS config file.
    '''

    # initialize the control variable
    OK = True

    # get the Trans-ABySS option dictionary
    transabyss_option_dict = xlib.get_option_dict(get_transabyss_config_file())

    # get the experiment identification
    experiment_id = transabyss_option_dict['identification']['experiment_id']

    # warn that the log window does not have to be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # check the Trans-ABySS config file
    log.write(f'{xlib.get_separator()}\n')
    log.write('Checking the {0} config file ...\n'.format(xlib.get_transabyss_name()))
    (OK, error_list) = check_transabyss_config_file(strict=True)
    if OK:
        log.write('The file is OK.\n')
    else:
        log.write('*** ERROR: The config file is not valid.\n')
        log.write('Please, correct this file or recreate it.\n')

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

    # check Trans-ABySS is installed
    if OK:
        (OK, error_list, is_installed) = xbioinfoapp.is_installed_anaconda_package(xlib.get_transabyss_anaconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_installed:
                log.write('*** ERROR: {0} is not installed.\n'.format(xlib.get_transabyss_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} installation could not be performed.\n'.format(xlib.get_transabyss_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # for each kmer value, build the process, copy it the cluster and run it
    if OK:

        # get the kmer list
        kmer = transabyss_option_dict['Trans-ABySS parameters']['kmer']
        kmer_list = xlib.split_literal_to_integer_list(kmer)
        
        # for each kmer value, do the tasks
        i = 1
        for kmer_value in kmer_list:

            # determine the run directory in the cluster
            log.write(f'{xlib.get_separator()}\n')
            log.write('Determining the run directory for kmer {0} in the cluster ...\n'.format(kmer_value))
            if i > 1:
                current_run_dir = '{0}-{1}'.format(xlib.get_cluster_current_run_dir(experiment_id, xlib.get_transabyss_code()), i)
            else:
                current_run_dir = '{0}'.format(xlib.get_cluster_current_run_dir(experiment_id, xlib.get_transabyss_code()))
            command = f'mkdir --parents {current_run_dir}'
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                log.write(f'The directory path is {current_run_dir}.\n')
            else:
                log.write(f'*** ERROR: Wrong command ---> {command}\n')
            i += 1

            # build the Trans-ABySS process script
            log.write(f'{xlib.get_separator()}\n')
            log.write('Building the process script {0} ...\n'.format(get_transabyss_process_script()))
            (OK, error_list) = build_transabyss_process_script(cluster_name, current_run_dir, kmer_value)
            if OK:
                log.write('The file is built.\n')
            if not OK:
                log.write('*** ERROR: The file could not be built.\n')
                break

            # upload the process script in the cluster
            log.write(f'{xlib.get_separator()}\n')
            log.write('Uploading the process script {0} in the directory {1} ...\n'.format(get_transabyss_process_script(), current_run_dir))
            cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_transabyss_process_script()))
            (OK, error_list) = xssh.put_file(sftp_client, get_transabyss_process_script(), cluster_path)
            if OK:
                log.write('The file id uploaded.\n')
            else:
                for error in error_list:
                    log.write(f'{error}\n')
                break

            # set run permision to the process script in the cluster
            log.write(f'{xlib.get_separator()}\n')
            log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transabyss_process_script())))
            command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_transabyss_process_script()))
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                log.write('The run permision is set on.\n')
            else:
                log.write(f'*** ERROR: Wrong command ---> {command}\n')

            # build the process starter
            log.write(f'{xlib.get_separator()}\n')
            log.write('Building the process starter {0} ...\n'.format(get_transabyss_process_starter()))
            (OK, error_list) = build_transabyss_process_starter(current_run_dir)
            if OK:
                log.write('The file is built.\n')
            if not OK:
                log.write('***ERROR: The file could not be built.\n')
                break

            # upload the process starter in the cluster
            log.write(f'{xlib.get_separator()}\n')
            log.write('Uploading the process starter {0} in the directory {1} ...\n'.format(get_transabyss_process_starter(), current_run_dir))
            cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_transabyss_process_starter()))
            (OK, error_list) = xssh.put_file(sftp_client, get_transabyss_process_starter(), cluster_path)
            if OK:
                log.write('The file is uploaded.\n')
            else:
                for error in error_list:
                    log.write(f'{error}\n')
                break

            # set run permision to the process starter in the cluster
            log.write(f'{xlib.get_separator()}\n')
            log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transabyss_process_starter())))
            command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_transabyss_process_starter()))
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                log.write('The run permision is set on.\n')
            else:
                log.write(f'*** ERROR: Wrong command ---> {command}\n')

            # submit the process
            log.write(f'{xlib.get_separator()}\n')
            log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transabyss_process_starter())))
            OK = xssh.submit_script(cluster_name, ssh_client, current_run_dir, os.path.basename(get_transabyss_process_starter()), log)

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

def check_transabyss_config_file(strict):
    '''
    Check the Trans-ABySS config file checking the all the options have right values.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        transabyss_option_dict = xlib.get_option_dict(get_transabyss_config_file())
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append('*** ERROR: The option dictionary could not be built from the config file')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in transabyss_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = transabyss_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "read_dataset_id"
            read_dataset_id = transabyss_option_dict.get('identification', {}).get('read_dataset_id', not_found)
            if read_dataset_id == not_found:
                error_list.append('*** ERROR: the key "read_dataset_id" is not found in the section "identification".')
                OK = False

        # check section "Trans-ABySS parameters"
        if 'Trans-ABySS parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Trans-ABySS parameters" is not found.')
            OK = False
        else:

            # check section "Trans-ABySS parameters" - key "threads"
            threads = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('threads', not_found)
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_int(threads, minimum=1):
                error_list.append('*** ERROR: the key "threads" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Trans-ABySS parameters" - key "length"
            length = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('length', not_found)
            if length == not_found:
                error_list.append('*** ERROR: the key "length" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_int(length, minimum=1):
                error_list.append('*** ERROR: the key "length" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Trans-ABySS parameters" - key "kmer"
            kmer = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('kmer', not_found)
            if kmer == not_found:
                error_list.append('*** ERROR: the key "kmer" is not found in the section Trans-ABySS parameters".')
                OK = False
            else:
                kmer_list = xlib.split_literal_to_integer_list(kmer)
                if kmer_list == []:
                    error_list.append('*** ERROR: the key "kmer" has to be an integer number, or an integer number list, greater than or equal to 1.')
                    OK = False
                else:
                    for kmer_item in kmer_list:
                        if not xlib.check_int(kmer_item, minimum=1):
                            error_list.append('*** ERROR: the key "kmer" has to be an integer number, or an integer number list, greater than or equal to 1.')
                            OK = False
                            break

            # check section "Trans-ABySS parameters" - key "cov"
            cov = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('cov', not_found)
            if cov == not_found:
                error_list.append('*** ERROR: the key "cov" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_int(cov, minimum=0):
                error_list.append('*** ERROR: the key "cov" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Trans-ABySS parameters" - key "eros"
            eros = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('eros', not_found)
            if eros == not_found:
                error_list.append('*** ERROR: the key "eros" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_int(eros, minimum=0):
                error_list.append('*** ERROR: the key "eros" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Trans-ABySS parameters" - key "seros"
            seros = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('seros', not_found)
            if seros == not_found:
                error_list.append('*** ERROR: the key "seros" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_int(seros, minimum=0):
                error_list.append('*** ERROR: the key "seros" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Trans-ABySS parameters" - key "gsim"
            gsim = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('gsim', not_found)
            if gsim == not_found:
                error_list.append('*** ERROR: the key "gsim" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_int(gsim, minimum=0):
                error_list.append('*** ERROR: the key "gsim" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Trans-ABySS parameters" - key "indel"
            indel = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('indel', not_found)
            if indel == not_found:
                error_list.append('*** ERROR: the key "indel" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_int(indel, minimum=0):
                error_list.append('*** ERROR: the key "indel" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Trans-ABySS parameters" - key "island"
            island = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('island', not_found)
            if island == not_found:
                error_list.append('*** ERROR: the key "island" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_int(island, minimum=0):
                error_list.append('*** ERROR: the key "island" has to be an integer number greater than or equal to 0.')
                OK = False

            # check section "Trans-ABySS parameters" - key "useblat"
            useblat = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('useblat', not_found)
            if useblat == not_found:
                error_list.append('*** ERROR: the key "useblat" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_code(useblat, get_useblat_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "useblat" has to be {0}.'.format(get_useblat_code_list_text()))
                OK = False

            # check section "Trans-ABySS parameters" - key "pid"
            pid = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('pid', not_found)
            if pid == not_found:
                error_list.append('*** ERROR: the key "pid" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_float(pid, minimum=0., maximum=1.):
                error_list.append('*** ERROR: the key "pid" has to be a float number between 0 and 1.')
                OK = False

            # check section "Trans-ABySS parameters" - key "walk"
            walk = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('walk', not_found)
            if walk == not_found:
                error_list.append('*** ERROR: the key "walk" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_float(walk, minimum=0., maximum=1.):
                error_list.append('*** ERROR: the key "walk" has to be a float number between 0 and 1.')
                OK = False

            # check section "Trans-ABySS parameters" - key "cleanup"
            cleanup = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('cleanup', not_found)
            if cleanup == not_found:
                error_list.append('*** ERROR: the key "cleanup" is not found in the section "Trans-ABySS parameters".')
                OK = False
            elif not xlib.check_code(cleanup, get_cleanup_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "cleanup" has to be {0}.'.format(get_cleanup_code_list_text()))
                OK = False

            # check section "Trans-ABySS parameters" - key "other_parameters"
            not_allowed_parameters_list = ['threads', 'length', 'kmer', 'cov', 'eros', 'seros', 'gsim', 'indel', 'island', 'useblat', 'pid', 'walk', 'cleanup']
            other_parameters = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('other_parameters', not_found)
            if other_parameters == not_found:
                error_list.append('*** ERROR: the key "other_parameters" is not found in the section "Trans-ABySS parameters".')
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
            format = transabyss_option_dict.get('library', {}).get('format', not_found)
            if format == not_found:
                error_list.append('*** ERROR: the key "format" is not found in the section "library".')
                OK = False
            elif not xlib.check_code(format, get_format_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "format" has to be {get_format_code_list_text()}.')
                OK = False

            # check section "library" - key "read_type"
            read_type = transabyss_option_dict.get('library', {}).get('read_type', not_found)
            if read_type == not_found:
                error_list.append('*** ERROR: the key "read_type" is not found in the section "library".')
                OK = False
            elif not xlib.check_code(read_type, get_read_type_code_list(), case_sensitive=False):
                error_list.append(f'*** ERROR: the key "read_type" has to be {get_read_type_code_list_text()}.')
                OK = False

        # check section "library-1"
        if 'library-1' not in sections_list:
            error_list.append('*** ERROR: the section "library-1" is not found.')
            OK = False

        # check all sections "library-n"
        for section in sections_list:

            if section not in ['identification', 'Trans-ABySS parameters', 'library']:

                # check than the section identification is like library-n 
                if not re.match('^library-[0-9]+$', section):
                    error_list.append(f'*** ERROR: the section "{section}" has a wrong identification.')
                    OK = False

                else:

                    # check section "library-n" - key "read_file_1"
                    read_file_1 = transabyss_option_dict.get(section, {}).get('read_file_1', not_found)
                    if read_file_1 == not_found:
                        error_list.append(f'*** ERROR: the key "read_file_1" is not found in the section "{section}"')
                        OK = False

                    # check section "library-n" - key "read_file_2"
                    read_file_2 = transabyss_option_dict.get(section, {}).get('read_file_2', not_found)
                    if read_file_2 == not_found:
                        error_list.append(f'*** ERROR: the key "read_file_2" is not found in the section "{section}"')
                        OK = False

    # warn that the Trans-ABySS config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_transabyss_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_transabyss_process_script(cluster_name, current_run_dir, kmer_value):
    '''
    Build the current Trans-ABySS process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the option dictionary
    transabyss_option_dict = xlib.get_option_dict(get_transabyss_config_file())

    # get the options
    experiment_id = transabyss_option_dict['identification']['experiment_id']
    read_dataset_id = transabyss_option_dict['identification']['read_dataset_id']
    threads = transabyss_option_dict['Trans-ABySS parameters']['threads']
    length = transabyss_option_dict['Trans-ABySS parameters']['length']
    cov = transabyss_option_dict['Trans-ABySS parameters']['cov']
    eros = transabyss_option_dict['Trans-ABySS parameters']['eros']
    seros = transabyss_option_dict['Trans-ABySS parameters']['seros']
    gsim = transabyss_option_dict['Trans-ABySS parameters']['gsim']
    indel = transabyss_option_dict['Trans-ABySS parameters']['indel']
    island = transabyss_option_dict['Trans-ABySS parameters']['island']
    useblat = transabyss_option_dict['Trans-ABySS parameters']['useblat']
    pid = transabyss_option_dict['Trans-ABySS parameters']['pid']
    walk = transabyss_option_dict['Trans-ABySS parameters']['walk']
    cleanup = transabyss_option_dict['Trans-ABySS parameters']['cleanup']
    other_parameters = transabyss_option_dict['Trans-ABySS parameters']['other_parameters']
    format = transabyss_option_dict['library']['format']
    read_type = transabyss_option_dict['library']['read_type']

    # get the sections list
    sections_list = []
    for section in transabyss_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build library files
    file_list = ''
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^library-[0-9]+$', section):
            read_file_1 = transabyss_option_dict[section]['read_file_1']
            read_file_1 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_1)
            file_list += read_file_1 + ' '
            if read_type.upper() == 'PE':
                read_file_2 = transabyss_option_dict[section]['read_file_2']
                read_file_2 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_2)
                file_list += read_file_2 + ' '
    file_list = file_list[:len(file_list) - 1]

    # set the transcriptome file name
    transcriptome_file = 'transabyss'

    # write the Trans-ABySS process script
    try:
        if not os.path.exists(os.path.dirname(get_transabyss_process_script())):
            os.makedirs(os.path.dirname(get_transabyss_process_script()))
        with open(get_transabyss_process_script(), mode='w', encoding='iso-8859-1', newline='\n') as script_file_id:
            script_file_id.write( '#!/bin/bash\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'SEP="#########################################"\n')
            script_file_id.write( 'export HOST_IP=`curl --silent checkip.amazonaws.com`\n')
            script_file_id.write( 'export HOST_ADDRESS="ec2-${HOST_IP//./-}-compute-1.amazonaws.com"\n')
            script_file_id.write( 'export AWS_CONFIG_FILE=/home/ubuntu/.aws/config\n')
            script_file_id.write( 'export AWS_SHARED_CREDENTIALS_FILE=/home/ubuntu/.aws/credentials\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('TRANSABYSS_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_transabyss_anaconda_code())))
            script_file_id.write( '{0}\n'.format('PATH=$TRANSABYSS_PATH:$PATH'))
            script_file_id.write( '{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            script_file_id.write( '{0}\n'.format('source activate {0}'.format(xlib.get_transabyss_anaconda_code())))
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
            script_file_id.write( '{0}\n'.format('function run_transabyss_process'))
            script_file_id.write( '{\n')
            script_file_id.write(f'    cd {current_run_dir}\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    /usr/bin/time \\\n')
            script_file_id.write(f'        --format="{xlib.get_time_output_format()}" \\\n')
            script_file_id.write( '{0}\n'.format('        transabyss \\'))
            script_file_id.write( '{0}\n'.format('            --threads {0} \\'.format(threads)))
            script_file_id.write( '{0}\n'.format('            --stage final \\'))
            if read_type.upper() == 'PE':
                script_file_id.write( '{0}\n'.format('            --pe {0} \\'.format(file_list)))
            else:
                script_file_id.write( '{0}\n'.format('            --se {0} \\'.format(file_list)))
            script_file_id.write( '{0}\n'.format('            --length {0} \\'.format(length)))
            script_file_id.write( '{0}\n'.format('            --kmer {0} \\'.format(kmer_value)))
            script_file_id.write( '{0}\n'.format('            --cov {0} \\'.format(cov)))
            script_file_id.write( '{0}\n'.format('            --eros {0} \\'.format(eros)))
            script_file_id.write( '{0}\n'.format('            --seros {0} \\'.format(seros)))
            script_file_id.write( '{0}\n'.format('            --gsim {0} \\'.format(gsim)))
            script_file_id.write( '{0}\n'.format('            --indel {0} \\'.format(indel)))
            script_file_id.write( '{0}\n'.format('            --island {0} \\'.format(island)))
            if useblat.upper() == 'YES':
                script_file_id.write( '{0}\n'.format('            --useblat \\'))
            script_file_id.write( '{0}\n'.format('            --pid {0} \\'.format(pid)))
            script_file_id.write( '{0}\n'.format('            --walk {0} \\'.format(walk)))
            script_file_id.write( '{0}\n'.format('            --outdir {0} \\'.format(current_run_dir)))
            if other_parameters.upper() == 'NONE':
                script_file_id.write( '{0}\n'.format('            --name {0}'.format(transcriptome_file)))
            else:
                script_file_id.write( '{0}\n'.format('            --name {0} \\'.format(transcriptome_file)))
                parameter_list = [x.strip() for x in other_parameters.split(';')]
                for i in range(len(parameter_list)):
                    if parameter_list[i].find('=') > 0:
                        pattern = r'^--(.+)=(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        parameter_value = mo.group(2).strip()
                        if i < len(parameter_list) - 1:
                            script_file_id.write(f'            --{parameter_name} {parameter_value} \\\n')
                        else:
                            script_file_id.write( '{0}\n'.format('            --{0} {1}'.format(parameter_name, parameter_value)))
                    else:
                        pattern = r'^--(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        if i < len(parameter_list):
                            script_file_id.write(f'            --{parameter_name} \\\n')
                        else:
                            script_file_id.write( '{0}\n'.format('            --{0}'.format(parameter_name)))
                    i += 1
            script_file_id.write( '    RC=$?\n')
            script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error transabyss $RC; fi'))
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
            process_name = f'{xlib.get_transabyss_name()} process'
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
            script_file_id.write( '{0}\n'.format('run_transabyss_process'))
            script_file_id.write( 'end\n')
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transabyss_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_transabyss_process_starter(current_run_dir):
    '''
    Build the starter of the current Trans-ABySS process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Trans-ABySS process starter
    try:
        if not os.path.exists(os.path.dirname(get_transabyss_process_starter())):
            os.makedirs(os.path.dirname(get_transabyss_process_starter()))
        with open(get_transabyss_process_starter(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '#!/bin/bash\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            file_id.write( '{0}\n'.format('{0}/{1} &>>{0}/{2}'.format(current_run_dir, os.path.basename(get_transabyss_process_script()), xlib.get_cluster_log_file())))
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transabyss_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_transabyss_config_file():
    '''
    Get the Trans-ABySS config file path.
    '''

    # assign the Trans-ABySS config file path
    transabyss_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_transabyss_code())

    # return the Trans-ABySS config file path
    return transabyss_config_file

#-------------------------------------------------------------------------------

def get_transabyss_process_script():
    '''
    Get the Trans-ABySS process script path in the local computer.
    '''

    # assign the Trans-ABySS script path
    transabyss_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_transabyss_code())

    # return the Trans-ABySS script path
    return transabyss_process_script

#-------------------------------------------------------------------------------

def get_transabyss_process_starter():
    '''
    Get the Trans-ABySS process starter path in the local computer.
    '''

    # assign the Trans-ABySS process starter path
    transabyss_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_transabyss_code())

    # return the Trans-ABySS starter path
    return transabyss_process_starter

#-------------------------------------------------------------------------------
    
def get_useblat_code_list():
    '''
    Get the code list of "useblat".
    '''

    return ['YES', 'NO']

#-------------------------------------------------------------------------------
    
def get_useblat_code_list_text():
    '''
    Get the code list of "useblat" as text.
    '''

    return str(get_useblat_code_list()).strip('[]').replace('\'','').replace(',', ' or')

#-------------------------------------------------------------------------------
    
def get_cleanup_code_list():
    '''
    Get the code list of "cleanup".
    '''

    return ['0', '1', '2', '3']

#-------------------------------------------------------------------------------
    
def get_cleanup_code_list_text():
    '''
    Get the code list of "cleanup" as text.
    '''

    return str(get_cleanup_code_list()).strip('[]').replace('\'','').replace(',', ' or')

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

if __name__ == '__main__':
     print('This file contains functions related to the Trans-ABySS process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
