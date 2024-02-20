from .run import MDrunner

import os
import uuid
import re
import tempfile

class MDrunnerK8s(MDrunner):
#	mdrun = 'echo Should not reach here, mdrun must be redefined in prehook.'
#	mdrun = 'sleep 10m'
	mdrun = 'gmx mdrun'
	mpiexec = 'mpiexec'

	def __init__(self,pvc=None,workdir=None,image='cerit.io/ljocha/gromacs:2023-2-plumed-2-9-afed-pytorch-model-cv',**kwargs):
		super().__init__(**kwargs)
		self.image = image

# heuristics to find PVC and working dir; can be overriden 
		if pvc is None:
			vol,_,_,_,_,mnt = os.popen('df .').readlines()[1].split()
			pvcid = re.search('pvc-[0-9a-z-]+',vol).group(0)
			pvc=os.popen(f'kubectl get pvc | grep {pvcid} | cut -f1 -d" "').read().rstrip()

			if workdir is None:
				workdir = os.path.relpath(os.getcwd(),mnt)

		if workdir is None:
			workdir = ''

		self.workdir = workdir
		self.pvc = pvc
		self.jobname = "gmx-" + str(uuid.uuid4())

	# start K8s job
	def prehook(self,cores=1,gpus=0,gputype='mig-1g.10gb',mem=4):
		job = f"""\
apiVersion: batch/v1
kind: Job
metadata:
  name: {self.jobname}
spec:
  backoffLimit: 0
  template:
    metadata:
      labels:
        job: {self.jobname}
    spec:
      restartPolicy: Never
      containers:
      - name: {self.jobname}
        image: {self.image}
        workingDir: /mnt/{self.workdir}
        command: 
        - sleep
        - 365d
        securityContext:
          runAsUser: 1000
          runAsGroup: 1000
          runAsNonRoot: true
          seccompProfile:
            type: RuntimeDefault
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL


        env:
        - name: 'OMP_NUM_THREADS'
          value: '{cores}'
        resources:
          requests:
            cpu: '{cores}'
            memory: {mem}Gi
            nvidia.com/{gputype}: {gpus}
          limits:
            cpu: '{cores}'
            memory: {mem}Gi
            nvidia.com/{gputype}: {gpus}
        volumeMounts:
        - name: vol-1
          mountPath: /mnt
      volumes:
      - name: vol-1
        persistentVolumeClaim:
          claimName: {self.pvc}
"""
		with tempfile.NamedTemporaryFile('w+') as y:
			y.write(job)
			y.flush()
			os.system(f'kubectl apply -f {y.name}')
			os.system(f'kubectl wait --for=condition=ready pod -l job={self.jobname}')



	# cleanup the K8s job
	def posthook(self):
		os.system(f'kubectl delete job/{self.jobname}')

	def commandline(self, **kwargs):
		return ['kubectl','exec','-ti',f'job/{self.jobname}','--'] + super().commandline(**kwargs)
