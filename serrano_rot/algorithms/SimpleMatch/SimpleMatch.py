import time
import json
import serrano_rot.algorithms.algorithmInterface as algorithmInterface


class SimpleMatch(algorithmInterface.AlgorithmInterface):

    def __init__(self, params):
        super().__init__(params)

    def launch(self):

        results = { "assignments":[] }
        replicas = 9

        params = self.get_input_parameters()
        deployment = params["deployment"]
        pods_per_cluster = params["pods_per_cluster"]
        
        uuid_part = deployment["deployment_uuid"].split("-")[-1]

        for deployment in deployment["description"]:
            if deployment["kind"] == "Deployment":
                deployment_name = "%s-%s" % (deployment["metadata"]["name"], uuid_part)
                if "replicas" in deployment["spec"]:
                    replicas = deployment["spec"]["replicas"]
                else:
                    replicas += 1

        # cluster_uuid with less assigned pods
        cluster_uuid = min(pods_per_cluster, key=lambda k: pods_per_cluster[k])

        results["assignments"] = [{"cluster_uuid": cluster_uuid, "replicas":replicas, "instructions": [{"metadata.name": deployment_name}]}]

        return json.dumps(results)

