#vim: ts=4 expandtab ai:
from .run import MDrunner

import os
import uuid
import re
import tempfile

class MDrunnerK8s(MDrunner):
#    mdrun = 'echo Should not reach here, mdrun must be redefined in prehook.'
#    mdrun = 'sleep 10m'
    mdrun = 'gmx mdrun'
    mpiexec = 'mpiexec'

    def __init__(self,pvc=None,workdir=None,image='cerit.io/ljocha/gromacs:2024-3-plumed-2-10-afed-pytorch-model-cv-2',mpi=1,omp=1,gpus=0,gputype='mig-1g.10gb',mem=4,jobname=None,**kwargs):
        super().__init__(**kwargs)
        self.image = image
        self.mpi = mpi
        self.omp = omp
        self.gpus = gpus
        self.gputype = gputype
        self.mem = mem

        mnt = ''

# heuristics to find PVC and working dir; can be overriden 
        if pvc is None:
            vol,_,_,_,_,mnt = os.popen('df .').readlines()[1].split()
            pvcid = re.search('pvc-[0-9a-z-]+',vol).group(0)
            pvc=os.popen(f'kubectl get pvc | grep {pvcid} | cut -f1 -d" "').read().rstrip()

            if workdir is None:
                workdir = os.path.relpath(os.getcwd(),mnt)
                print(f'mnt = {mnt}, workdir = {workdir}')

        if workdir is None:
            workdir = ''

        self.workdir = workdir
        self.pvc = pvc
        self.mnt = mnt
        if jobname is None:
            self.jobname = "gmx-" + str(uuid.uuid4())
        else:
            self.jobname = jobname

    # start K8s job
    def prehook(self,retry=1):
#        if cores is not None and cores != mpi * omp:
#            raise ValueError(f'cores ({cores}) != mpi ({mpi}) * omp ({omp})')
#        if cores is None:
#            cores = mpi * omp
        cores = self.mpi * self.omp

        with open(f'{self.mnt}/{self.workdir}/{self.jobname}.out','w') as out:
            out.write('Log created\n')

        with open(f'{self.mnt}/{self.workdir}/{self.jobname}.sh','w') as script:
            script.write(f'''#!/bin/bash

while [ ! -f {self.jobname}.cmd ]; do
    sleep 1
done

exec >>{self.jobname}.out 2>>{self.jobname}.out
echo Starting {self.jobname} payload >&2
exec $(cat {self.jobname}.cmd)
''')
        os.chmod(f'{self.mnt}/{self.workdir}/{self.jobname}.sh',0o755)

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
        - /mnt/{self.workdir}/{self.jobname}.sh
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
          value: '{self.omp}'
        resources:
          requests:
            cpu: '{cores}'
            memory: {self.mem}Gi
            nvidia.com/{self.gputype}: {self.gpus}
          limits:
            cpu: '{cores}'
            memory: {self.mem}Gi
            nvidia.com/{self.gputype}: {self.gpus}
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
#            for _ in range(retry):
#                s=os.system(f'kubectl wait --for=condition=ready pod -l job={self.jobname} --timeout=3600s')
#                if os.WEXITSTATUS(s) == 0:
#                    break



#    def posthook(self):
##        os.system(f'kubectl delete job/{self.jobname}')
#        os.remove(f'{self.mnt}/{self.workdir}/{self.jobname}.sh')
#        os.remove(f'{self.mnt}/{self.workdir}/{self.jobname}.cmd')
##        os.remove(f'{os.getcwd()}/{self.workdir}/{self.jobname}.out')

    def commandline(self, **kwargs):
#        return ['kubectl','exec','-ti',f'job/{self.jobname}','--'] + super().commandline(**kwargs)
        with open(f'{self.mnt}/{self.workdir}/{self.jobname}.tmp','w') as cmd:
            cmd.write(" ".join(super().commandline(**kwargs)))

        os.rename(f'{self.mnt}/{self.workdir}/{self.jobname}.tmp',f'{self.mnt}/{self.workdir}/{self.jobname}.cmd')
#        return [ 'tail', '-f', f'{self.mnt}/{self.workdir}/{self.jobname}.out' ]
        return ['kubectl','get',f'job/{self.jobname}']

    def run(self,**kwargs):
#    mdrunner.run(pre={'omp':ompthreads,'mpi':mpiranks,'gpus':gpus, 'retry':10 }, mdrunargs={**kwargs,'ntomp':ompthreads,'pin':'on'},ncores=mpiranks)
        return super().run(mdrunargs = { **kwargs, 'ntomp': self.omp, 'pin':'on'}, ncores=self.mpi)


    def kill(self):
        os.remove(f'{self.mnt}/{self.workdir}/{self.jobname}.sh')
        os.remove(f'{self.mnt}/{self.workdir}/{self.jobname}.cmd')
        os.system(f'kubectl delete job/{self.jobname}')
        
    def log(self,tail=0):
        with open(f'{self.mnt}/{self.workdir}/{self.jobname}.out') as log:
            for l in list(log)[-tail:]:
                print(l,end='')
