# Copyright 2012 OpenStack Foundation.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import logging

from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.common import exceptions

class PolicyNotFound(exceptions.NotFound):
    message = "Policy of type %(policy) not found"
    
class ValueNotValid(exceptions.NeutronCLIError):
    message = ("Value %(value) for %(policy) invalid")


class ListQoS(neutronV20.ListCommand):
    resource = 'qos'
    log = logging.getLogger(__name__ + '.ListQoS')

    list_columns = ['id', 'name', 'description']


class ShowQoS(neutronV20.ShowCommand):
    resource = 'qos'
    log = logging.getLogger(__name__ + '.ShowQoS')


class DeleteQoS(neutronV20.DeleteCommand):
    resource = 'qos'
    log = logging.getLogger(__name__ + '.DeleteQoS')


def _check_true_false(value):
    if value.encode('UTF-8').lower() == "true":
        return "true"
    else:
        return "false"

class CreateQoS(neutronV20.CreateCommand):
    resource = 'qos'
    log = logging.getLogger(__name__ + '.CreateQoS')
    
    policy_type_allowed = ['dscp', 'ingress_rate', 'egress_rate', 'burst_percent']
    
    def _validate_policy(self, policies):
        for parg in policies:
            args = parg.split('=')
            if not any(args[0] in s for s in self.policy_type_allowed):
                raise exceptions.NeutronClientException(message="%s is not a valid policy" % args[0])

    def add_known_arguments(self, parser):
        #parser.add_argument('--type',
        #                    help="QoS Type", choices=['dscp', 'ingress_rate', 'egress_rate', 'burst_percent'])
        parser.add_argument('--policies',
                            help='Set of policies for a QoS. Avaible policies: dscp, ingress_rate, egress_rate, burst_percent', nargs='*')
        parser.add_argument('--description', help="Description for the QoS")
        parser.add_argument('--default', help="if True this policy will be used when a new port will be create. Only one default is admitted.", 
                            nargs=1, choices=['true', 'false'], required=True )
        parser.add_argument('--public', help="If true all users can see and apply this policy.", 
                            nargs=1, choices=['true', 'false'], required=True )
        parser.add_argument('--name', help="Name of QoS", required=True)

    def args2body(self, parsed_args):
        body = {self.resource: {}}

        body[self.resource]['policies'] = {}
            
        if parsed_args.policies:
            #try:
            self._validate_policy(parsed_args.policies)
            #except:
            #    return {}
            for parg in parsed_args.policies:
                args = parg.split('=')
                body[self.resource]['policies'][args[0]] = args[1]
       # if parsed_args.type:
       #     body[self.resource]['type'] = parsed_args.type
        if parsed_args.description:
            body[self.resource]['description'] = parsed_args.description
        if parsed_args.name:
            body[self.resource]['name'] = parsed_args.name
        if parsed_args.tenant_id:
            body[self.resource].update({'tenant_id': parsed_args.tenant_id})
        if parsed_args.default:
            body[self.resource]['default'] = _check_true_false(parsed_args.default[0])
            #body[self.resource]['default'] = "True" if parsed_args.default[0].encode('UTF-8')== "true" else "False" 
        if parsed_args.public:
            body[self.resource]['public'] = _check_true_false(parsed_args.public[0])
        return body
    
class UpdateQoS(neutronV20.UpdateCommand):
    resource = 'qos'
    log = logging.getLogger(__name__ + '.UpdateQoS')
    
    def add_known_arguments(self, parser):
        parser.add_argument('--policies',
                            help='Set of policies for a QoS. Avaible policies: dscp, ingress_rate, egress_rate, burst_percent', nargs='*')

    def args2body(self, parsed_args):
        body = {self.resource: {}}
        body[self.resource]['policies'] = {}
        if parsed_args.policies:
            for parg in parsed_args.policies:
                args = parg.split('=')
                body[self.resource]['policies'][args[0]] = args[1]
        return body
    
class QosAssociate(neutronV20.UpdateCommand):
    resource = 'qos'
    log = logging.getLogger(__name__ + '.QoSAssociate')
    
    def add_known_arguments(self, parser):
        parser.add_argument('--tenant',
                        help='Tenant id to associate with qos', required=True)
#        parser.add_argument('--qos',
#                        help='Qos id to associate with tenant', required=True)
        return parser
        
    def args2body(self, parsed_args):
        body = {self.resource: {}}
        body[self.resource]["association"] = "associate"
        if parsed_args.tenant:
            body[self.resource]['tenant'] = parsed_args.tenant

        return body

class QosDisassociate(neutronV20.UpdateCommand):
    resource = 'qos'
    log = logging.getLogger(__name__ + '.QoSDisassociate')
    
    def add_known_arguments(self, parser):
        parser.add_argument('--tenant',
                        help='Tenant id to disassociate with qos', required=True)
#        parser.add_argument('--qos',
#                        help='Qos id to associate with tenant', required=True)
        return parser
        
    def args2body(self, parsed_args):
        body = {self.resource: {}}
        body[self.resource]["association"] = "disassociate"
        if parsed_args.tenant:
            body[self.resource]['tenant'] = parsed_args.tenant

        return body
    
class ListTenantList(neutronV20.ListCommand):
    resource = 'qosassociate'
    log = logging.getLogger(__name__ + '.ListQosAssociate')

    list_columns = ['qos_id', 'tenant_id']