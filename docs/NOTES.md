# DevSecOps Platform — Learning Journal
**Author:** Shambhavi
**Start Date:** June 2026

## Progress Tracker
- [x] Module 0: Environment Setup — In Progress
- [ ] Module 1: Kubernetes Fundamentals
- [ ] Module 2: Kubernetes Networking
- [ ] Module 3: Kubernetes Storage
- [ ] Module 4: Docker Deep Dive
- [ ] Module 5: Helm
- [ ] Module 6: Terraform Advanced
- [ ] Module 7: GitHub Actions
- [ ] Module 8: DevSecOps Tools
- [ ] Module 9: ArgoCD & GitOps
- [ ] Module 10: Prometheus
- [ ] Module 11: Grafana
- [ ] Module 12: Loki
- [ ] Module 13: OpenTelemetry
- [ ] Module 14: Production Architecture
- [ ] Module 15: Final Capstone

## MODULE 0: Environment Setup
### Date: June 15, 2026

### What I Did
- Installed WSL2 Ubuntu on Windows
- Installed Docker Desktop + enabled WSL2 integration
- Fixed docker permission denied error
- Successfully ran first Docker container

### Commands Learned
- wsl --install -d Ubuntu → Install Ubuntu on WSL2
- sudo apt update → Update package list
- sudo usermod -aG docker $USER → Add user to docker group
- docker run hello-world → Test Docker
- uname -a → Check Linux kernel
- groups → Show user groups

### Errors Faced
**Error:** permission denied on docker.sock
**Cause:** User not in docker group
**Fix:** sudo usermod -aG docker $USER then wsl --shutdown

**Error:** Docker not found in WSL2
**Cause:** WSL Integration not enabled in Docker Desktop
**Fix:** Docker Desktop > Settings > Resources > WSL Integration > Ubuntu ON

### Interview Q&A
Q: Difference between Docker image and container?
A: Image is blueprint (like Python class), container is running instance (like object)

Q: What is /var/run/docker.sock?
A: Unix socket file for Docker client-daemon communication

Q: Why WSL2 for DevOps on Windows?
A: DevOps tools are Linux-native. WSL2 gives real Linux kernel on Windows.


### Kind Cluster Created Successfully
**Date:** June 16, 2026

**Issue faced:** TLS handshake timeout pulling kindest/node image from Docker Hub
**Cause:** ISP/network DNS resolution issue with Docker Hub
**Fix:** Changed DNS to Google DNS (8.8.8.8, 8.8.4.4) via /etc/resolv.conf, then docker pull succeeded

**Cluster verified:**
- kubectl cluster-info -> control plane + CoreDNS reachable
- kubectl get nodes -> 1 node, Ready, v1.34.0
- kubectl get pods -A -> 9 system pods running (coredns x2, etcd, kindnet, kube-apiserver, kube-controller-manager, kube-scheduler, kube-proxy, local-path-provisioner)

### Concepts Learned
- A kind cluster = a Docker container acting as a full K8s node
- kube-system namespace holds Kubernetes' own internal components
- etcd = cluster's database (stores all object state)
- API server = entry point for all kubectl commands
- Scheduler = decides which node runs a new pod
- Controller manager = continuously reconciles desired state vs actual state
- CNI (Container Network Interface) = gives pods networking/IP addresses
- kubectl context = which cluster kubectl is currently talking to

### Interview Q&A
Q: What are the core components of the Kubernetes control plane?
A: API server (entry point), etcd (cluster database), scheduler (pod placement), controller manager (reconciliation loop)

Q: What is etcd and why does it matter?
A: etcd is a distributed key-value store holding all cluster state. If etcd is lost without backup, the entire cluster's configuration is lost.

Q: What does kubectl actually do when you run a command?
A: kubectl sends a REST API request to the kube-apiserver, which reads/writes to etcd and triggers controllers/scheduler as needed.


## MODULE 1: Kubernetes Fundamentals
### Date: June 16, 2026

### What I Did
- Created my first Pod manifest (k8s/base/pod.yaml) running nginx:1.27-alpine
- Applied it with kubectl apply -f
- Watched Pod go from Pending -> ContainerCreating -> Running
- Used kubectl describe pod to read the full Events timeline

### Concepts Learned

**Pod Lifecycle (the 5 events, in order):**
1. Scheduled - Scheduler assigns Pod to a node
2. Pulling - kubelet starts downloading the container image
3. Pulled - image download finished
4. Created - kubelet creates the container from the image
5. Started - container process begins running

**Kubernetes is declarative, not imperative**
- Docker: "run this container now" (one-time command)
- Kubernetes: "I want this Pod to exist" (continuously enforced desired state)

**YAML structure of a Pod:**
- apiVersion: which API group/version this object belongs to (v1 for core objects like Pod)
- kind: type of object (Pod, Deployment, Service, etc.)
- metadata.name: unique name for the object
- metadata.labels: key-value tags used by Kubernetes to SELECT groups of objects (critical for Services later)
- spec: the desired state (what I want)
- spec.containers[].image: which Docker image to run
- spec.containers[].ports: documents the port the app listens on (does not expose it externally by itself)

**Pod Conditions (debugging checklist):**
- PodScheduled, Initialized, ContainersReady, Ready, PodReadyToStartContainers
- Whichever one is False tells you exactly where in the lifecycle the Pod is stuck

**Pod got its own internal IP (from CNI/kindnet)**
- Only reachable INSIDE the cluster, not from outside (need a Service for that)

**QoS Class: BestEffort** appears when no CPU/memory requests/limits are set on the container - lowest scheduling priority under resource pressure

### Commands Learned
- kubectl apply -f <file>.yaml -> create/update objects from YAML
- kubectl get pods -> list pods, quick status check
- kubectl describe pod <name> -> full details + Events timeline (main debugging tool)

### Interview Q&A
Q: What is a Pod in Kubernetes?
A: The smallest deployable unit in Kubernetes. Wraps one or more containers that share network namespace and storage. Usually one container per Pod in practice.

Q: Walk me through what happens when you apply a Pod manifest.
A: kubectl sends the YAML to the API server, which validates and stores it in etcd. The Scheduler picks a node. The kubelet on that node pulls the image, creates the container, and starts it. Events show: Scheduled -> Pulling -> Pulled -> Created -> Started.

Q: How do you debug a Pod stuck in Pending or ContainerCreating?
A: Run kubectl describe pod <name> and read the Events section at the bottom - it shows the real-time story of what Kubernetes attempted and where it's stuck (e.g., image pull failure, scheduling failure, insufficient resources).

Q: What is the difference between declarative and imperative infrastructure management?
A: Imperative means running explicit commands to make changes happen once. Declarative means describing the desired end state, and a controller continuously works to keep reality matching that state - this is Kubernetes' core model.


### Real Incident: Cluster appeared down after terminal/Docker restart
**Date:** June 17, 2026

**Symptom:** kubectl commands failed with "connection refused" on 127.0.0.1:<port>
**Cause:** kind cluster runs as a Docker container. When Docker Desktop wasn't running, that container (and the whole cluster inside it) was stopped too.
**Fix:** Started Docker Desktop again - kind's underlying container resumed, cluster came back with all previous state intact (etcd persisted on disk inside the container).

**Observed:** nginx-pod showed RESTARTS: 1, AGE: 28h - proof that kubelet automatically restarted the container inside the Pod once the node was healthy again (RestartPolicy: Always is the default).

### Lesson Learned
- A kind cluster is only "up" while its underlying Docker container is running
- Docker Desktop must be running BEFORE using kubectl, every session
- Pod's RestartPolicy (default: Always) restarts a crashed/stopped container automatically - this is a small preview of self-healing even at the Pod level, separate from Deployment-level self-healing


### Date: June 18, 2026 (continued)

### Concepts Learned (continued)
- Cascading deletion via ownerReferences: every child object (ReplicaSet, Pod) stores
  a hidden reference to its parent. Kubernetes Garbage Collector watches these and
  auto-deletes orphaned children the moment a parent is removed.
  - Proved live: `kubectl delete deployment nginx-deployment` -> ReplicaSet deleted
    instantly -> all 3 Pods went `Terminating` -> fully gone within ~30s grace period.
- Scaling replicas - two methods:
  1. Imperative: `kubectl scale deployment <name> --replicas=N` - fast, no YAML touch,
     but NOT persisted - gets silently overwritten on next `kubectl apply` if the
     YAML file doesn't match.
  2. Declarative: edit `replicas:` in YAML, then `kubectl apply -f file.yaml` - the
     correct way for production since YAML-in-Git is the source of truth.
  - Proved live: scaled to 5 imperatively -> ran `kubectl apply` with old YAML
    (replicas: 3) -> got silently reverted back to 3. This is the core reason
    GitOps tools like ArgoCD exist (force Git as continuous source of truth).
- ReplicaSet hash (e.g. nginx-deployment-6f9664446b) is generated from the Pod
  template (image, labels) - changes only when the template changes, NOT when
  replica count changes. Confirmed: hash stayed identical before/after scaling 3->5.
- Lesson: resources created via bare `kubectl create` (imperative) leave no file
  behind - if deleted, must be recreated from memory. Going forward: always create
  K8s resources from YAML files saved in repo (k8s/base/), never ad-hoc.

### Commands Learned (continued)
- `kubectl delete deployment <name>` - cascade deletes owned ReplicaSet + Pods
- `kubectl scale deployment <name> --replicas=N` - imperative scale
- `sed -i 's/replicas: 3/replicas: 5/' file.yaml` - inline find/replace in a file
- `find . -iname "*pattern*"` - search files by name, case-insensitive

### Errors / Anomalies Faced
- Pods showed `RESTARTS 1 (Xm ago)` before any manual action was taken - likely
  caused by Docker Desktop/WSL2 restarting underneath kubelet. Pod object survived
  (kubelet restarted the container in place). Noted for monitoring, not yet root-caused.

### Date: June 18, 2026 (Module 1 wrap-up)

### Concepts Learned (continued)
- Services: stable virtual IP + DNS name that routes traffic to Pods matching a
  label selector, decoupling clients from ever-changing Pod IPs. ClusterIP type =
  internal-only (no external access yet, covered in Module 2 Networking).
- ConfigMap: externalizes non-sensitive config (e.g. custom HTML) so it can be
  changed without rebuilding the container image. Mounted as a volume, overriding
  files inside the container filesystem.
- Secret: same mechanism as ConfigMap, but for sensitive data. IMPORTANT: only
  base64-ENCODED by default, NOT encrypted - trivially reversible
  (`echo <value> | base64 -d`). Real protection needs etcd encryption-at-rest or
  an external vault (Module 8 territory).
- Confirmed live: changing the Pod template (adding env vars + volume mounts)
  triggers the Deployment to create a brand NEW ReplicaSet and do a rolling
  update, while the OLD ReplicaSet is kept at 0 replicas as a rollback point
  (`kubectl get rs` showed both side by side).

### Commands Learned (continued)
- `kubectl expose deployment <name> --port=P --target-port=P --type=ClusterIP --name=<svc>`
- `kubectl run <pod> --image=<img> --restart=Never --rm -it -- <cmd>` - quick disposable
  test pod, auto-deleted after the command finishes
- `kubectl apply -f <configmap.yaml>` / `<secret.yaml>`
- `echo "<base64string>" | base64 -d` - decode a Secret value
- `kubectl exec <pod> -- env | grep <VAR>` - check env vars inside a running container
- `kubectl rollout status deployment/<name>` - watch a rolling update complete
- `kubectl get rs` - see old vs new ReplicaSets side by side during/after a rollout

### Mistakes / Lessons Learned (continued)
- Tried stripping fields from `kubectl -o yaml` output using `grep -v` - produced
  malformed YAML with duplicate keys. It happened to still work because YAML
  silently resolves duplicate keys by taking the last one, but this is fragile
  and should never be relied on. Lesson: write YAML by hand or use a proper
  tool, never grep-strip structured data.

### Module 1 - Practical Assignment Given
- Build an independent httpd-based mini-stack (ConfigMap + Secret + Deployment +
  Service) without guided help, to self-test retention. [STATUS: pending]

### Module 1 - Resume Bullet
"Deployed and managed containerized workloads on Kubernetes, implementing
Deployments with rolling updates and ReplicaSet-based self-healing, exposed
internal services via ClusterIP networking, and externalized application
configuration and credentials using ConfigMaps and Secrets to eliminate
hardcoded config from container images."

### Module 1 - Interview Q&A (continued)
- Q: What happens when you delete a Deployment? A: Cascading deletion via
  ownerReferences - Deployment -> ReplicaSet -> Pods all get removed automatically
  by the garbage collector.
- Q: Why does Deployment delegate to ReplicaSet? A: Separation of concerns -
  ReplicaSet just maintains pod count; Deployment manages rollout history and
  rollback by creating new ReplicaSets on template changes.
- Q: ConfigMap vs Secret? A: Same mechanism, Secret meant for sensitive data,
  but only base64-encoded NOT encrypted by default.
- Q: How does a Service find its Pods? A: Label selector matching, continuously
  and dynamically, regardless of Pod IP churn.

### MODULE 1: STATUS - COMPLETE (June 18, 2026)

### Real Incident: NodePort connection reset, then worked after a short wait
**Date:** June 18, 2026

**Symptom 1:** curl http://172.18.0.2:30080 -> Could not connect (timeout)
**Cause 1:** kind cluster was created WITHOUT mapping port 30080 from the Docker 
container to the host machine. Only port 6443 (API server) was mapped by default.
**Fix 1:** Recreated the kind cluster using a kind config file with extraPortMappings, 
explicitly mapping containerPort 30080 -> hostPort 30080.

kind-config.yaml used:
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 30080
        protocol: TCP

**Symptom 2:** After recreating cluster + reapplying YAMLs, curl http://localhost:30080 
gave "Connection reset by peer"
**Diagnosis:** Checked kubectl describe svc nginx-nodeport -> Endpoints showed 6 healthy 
pod IPs, so Service-to-Pod wiring was correct. Docker port mapping was also confirmed 
correct via docker ps. This ruled out config errors.
**Cause 2:** kube-proxy had not yet finished programming the network rules (iptables/
nftables) for the newly created Service - a timing/race condition right after Service 
creation, not a configuration mistake.
**Fix 2:** Waited a few seconds (sleep 5) then retried curl -> got HTTP 200 OK with 
nginx welcome page.

### Lesson Learned
- kind clusters do NOT expose NodePort ports to the host by default - must explicitly 
  configure extraPortMappings in a kind config file at cluster creation time
- After creating a Service, kube-proxy needs a short moment to program network rules 
  before traffic will route correctly - give it a few seconds before debugging further
- Debugging order that worked: confirm Docker-level port mapping (docker ps) -> confirm 
  Service has Endpoints (kubectl describe svc) -> confirm with verbose curl (curl -v) 
  to see exact point of failure

### Commands Learned
- kind create cluster --config <file>.yaml -> create cluster with custom port mappings/config
- kubectl apply -f <directory>/ -> apply ALL yaml files inside a folder at once
- curl -v <url> -> verbose curl, shows full connection handshake details for debugging
- docker ps -> shows port mappings for kind's underlying container


### Real Incident: Duplicate Deployment files caused unexpected pod count
**Date:** June 18, 2026

**Symptom:** kubectl get pods showed 5 nginx pods + 1 stray nginx-pod, expected 3
**Cause:** Two separate YAML files (deployment.yaml with replicas:3, and 
nginx-deployment.yaml with replicas:5) both defined a Deployment named 
"nginx-deployment" with the same selector (app: nginx). Running 
kubectl apply -f k8s/base/ applied both files - the later one (nginx-deployment.yaml, 
replicas:5) won. The old standalone pod.yaml (bare nginx-pod) was also still in the 
folder and got reapplied, adding a 6th matching pod under the same label.
**Fix:** Identified nginx-deployment.yaml as the intentional, up-to-date version 
(it included Secret and ConfigMap wiring). Deleted the redundant deployment.yaml and 
pod.yaml, deleted the stray nginx-pod, reapplied the folder - left with exactly 5 
correct pods.

### Lesson Learned
- Never have two manifests defining objects with the same name/selector in the same 
  folder - kubectl apply -f <folder>/ applies every file, last one applied wins for 
  conflicting fields
- Keep k8s/base/ as a single source of truth per object - one file per Deployment/
  Service/etc, not multiple draft versions left lying around
- Real production practice: delete or move old/draft manifest files out of the 
  folder that gets applied, don't just leave them - they will get applied too


### Verified: ConfigMap and Secret working end-to-end
**Date:** June 18, 2026

- Decoded Secret manually (echo | base64 -d) -> confirmed base64 is encoding, NOT 
  encryption - anyone with read access to the Secret object can trivially reverse it
- Verified DB_PASSWORD env var was correctly injected into the running container via 
  kubectl exec -- env
- Verified ConfigMap-provided index.html was correctly mounted at 
  /usr/share/nginx/html/index.html inside the container, overriding nginx's default page
- Verified full request path works: curl localhost:30080 -> kind port mapping -> 
  kube-proxy -> Service (nginx-nodeport) -> Pod -> ConfigMap file -> response

### Concepts Learned
- ConfigMap: stores non-sensitive config data as key-value pairs, can be mounted as 
  files (via volumes) or injected as env vars
- Secret: same mechanism as ConfigMap but for sensitive data - values are base64 
  ENCODED (not encrypted) - production setups need extra tools (Vault, sealed-secrets, 
  cloud KMS) for real security
- volumeMounts + volumes: the two-part mechanism to mount a ConfigMap/Secret as files 
  inside a container (volumes defines the source, volumeMounts defines where it lands)
- env.valueFrom.secretKeyRef: the mechanism to inject a single Secret key as an 
  environment variable

### Interview Q&A
Q: What's the difference between a ConfigMap and a Secret?
A: Mechanically nearly identical - both store key-value config data and can be mounted 
as files or env vars. The difference is intent and encoding: Secrets are meant for 
sensitive data and values are base64 encoded, but that is NOT encryption - anyone with 
API access to read the Secret can decode it instantly. Real security needs additional 
tooling (Vault, sealed-secrets, KMS-backed secrets).

Q: How do you inject configuration into a Pod without baking it into the Docker image?
A: Two ways - mount a ConfigMap/Secret as a file using volumes + volumeMounts, or 
inject specific keys as environment variables using env.valueFrom.configMapKeyRef or 
secretKeyRef. This decouples config from the image, so the same image can run in 
dev/stage/prod with different config.


## MODULE 2: Kubernetes Networking
### Date: June 18, 2026

### What I Did
- Already touched NodePort Services hands-on during Module 1 cleanup (debugging 
  connection reset, port mapping issue with kind)
- Created a temporary Pod (kubectl run --rm) to test Pod-to-Pod DNS resolution
- Successfully curled "http://nginx-service" by NAME (no IP) from inside another Pod, 
  proving CoreDNS resolves Service names to ClusterIPs automatically

### Concepts Learned

**Service Types:**
- ClusterIP (default) - internal only, most common type for service-to-service calls
- NodePort - exposes a fixed port on every node's IP, reachable from outside the cluster
- LoadBalancer - asks cloud provider for a real external load balancer (only works on 
  real cloud, not local kind without extra tooling)
- ExternalName - maps a Service to an external DNS name, rare/niche

**How a Service finds Pods:**
- Service has a "selector" (label match, e.g. app=nginx)
- Service continuously watches for Pods matching that selector
- Matching Pod IPs become the Service's "Endpoints" (kubectl describe svc shows this)
- kube-proxy programs network rules (iptables/nftables) to load-balance traffic 
  across those Endpoints

**Cluster DNS (CoreDNS):**
- Any Pod can reach a Service by name alone: http://<service-name> (same namespace) 
  or http://<service-name>.<namespace>.svc.cluster.local (any namespace, fully qualified)
- This is why microservices never hardcode IPs - they call each other by Service name

**kubectl run --rm -it --restart=Never** - creates a temporary one-off Pod for quick 
testing/debugging, auto-deletes after running. Useful pattern for testing connectivity 
without leaving junk Pods around.

### Commands Learned
- kubectl run <name> --image=<image> --rm -it --restart=Never -- <command> 
  -> spin up a temporary test Pod, run one command, auto-cleanup
- kubectl describe svc <name> -> shows Selector and live Endpoints (critical debugging tool)

### Interview Q&A
Q: How does a Kubernetes Service know which Pods to send traffic to?
A: Through label selectors. The Service has a selector (e.g. app=nginx), and 
continuously watches the cluster for any Pod whose labels match. Matching Pod IPs 
become the Service's Endpoints, and kube-proxy load-balances traffic across them.

Q: How do two Pods in the same cluster communicate with each other?
A: Usually via a Service, calling it by DNS name (resolved by CoreDNS) rather than by 
direct Pod IP, since Pod IPs change every time a Pod restarts. CoreDNS resolves the 
Service name to its stable ClusterIP.

Q: What's the difference between ClusterIP, NodePort, and LoadBalancer?
A: ClusterIP is internal-only (default). NodePort opens a fixed port on every node's 
IP, making it reachable from outside the cluster. LoadBalancer requests an actual 
external load balancer from the cloud provider - it doesn't work on local clusters 
like kind without extra tooling.


### Real Incident: Ingress controller Pod had a temporary FailedMount on startup
**Date:** June 18, 2026

**Symptom:** kubectl describe pod showed "Warning FailedMount: secret 
ingress-nginx-admission not found" repeated 6 times over ~94 seconds
**Cause:** Race condition within the official ingress-nginx install manifest itself - 
the Controller Deployment tried to mount a Secret (webhook-cert) that gets created by 
a separate Job (ingress-nginx-admission-create) in the same manifest. The Deployment 
started slightly before that Job finished creating the Secret.
**Resolution:** kubelet automatically retried the mount every ~15s until the Secret 
existed, then mounted successfully, created the container, and started it - no manual 
fix needed. Self-resolved within ~95 seconds.

### Lesson Learned
- Not every Warning in kubectl describe means something is broken - some resolve 
  automatically as dependent resources finish being created (race conditions are 
  common when manifests bundle multiple interdependent objects like Deployments + Jobs)
- Reading the FULL Events timeline (not just the latest line) tells the complete story: 
  Scheduled -> FailedMount (x6, retrying) -> Pulling -> Pulled -> Created -> Started -> RELOAD
- New namespace observed: ingress-nginx - confirms namespaces are used to logically 
  group/isolate related objects within one physical cluster (similar to kube-system)


### Verified: Ingress working end-to-end
**Date:** June 18, 2026

- Full request path proven: curl localhost:8080 -> kubectl port-forward tunnel ->
  ingress-nginx-controller Service -> Ingress Controller Pod -> matched Ingress rule
  (path "/" -> nginx-service:80) -> nginx-service -> nginx Pod -> ConfigMap HTML response
- Confirmed: cluster's kind config only maps host ports 30080 and 6443 (per docker ps),
  NOT 80/443 - so the Ingress controller's hostPort 80/443 bindings aren't reachable
  directly from Windows. port-forward used as a workaround for local testing.
- Lesson: kubectl port-forward is a BLOCKING foreground process - pressing Ctrl+C kills
  the tunnel immediately. To keep testing in the same terminal, run it backgrounded
  with `&` and redirect output to a log file, then `kill %1` (or `jobs` to find the PID)
  when done.


### Verified: NetworkPolicy selective enforcement (corrected understanding)
**Date:** June 18, 2026

- IMPORTANT CORRECTION: initially assumed kindnet (kind's default CNI) does NOT
  enforce NetworkPolicies (true for older kind/kindnet versions, widely documented).
  Live-tested on this cluster (kind v0.30.0) and found NetworkPolicy enforcement
  DOES work - kindnet added a native NetworkPolicy controller in recent versions.
  Lesson: always verify against the actual running version, docs/blog posts can be
  outdated for fast-moving tools.
- Proved deny-all policy (ingress: []) blocks ALL incoming traffic to selected Pods
- Proved selective allow policy: Pods labeled app=nginx only accept traffic from
  Pods labeled access=true. Unlabeled test Pod -> wget timeout (denied). Pod created
  with --labels="access=true" -> succeeded (allowed). Real microsegmentation working.

### Commands Learned (continued)
- kubectl run <name> --image=<img> --rm -it --restart=Never --labels="key=value" -- <cmd>
  -> spin up a temporary Pod WITH a custom label, useful for testing NetworkPolicy
  selectors without creating a permanent YAML file
- kubectl delete networkpolicy <name>
- kubectl get networkpolicy

### MODULE 2: Kubernetes Networking - Practical Assignment Given
- Two-app setup: httpd Service + path-based Ingress routing (/app2) + NetworkPolicy
  restricting httpd to access=true labeled Pods only. [STATUS: pending]

### MODULE 2: Resume Bullet
"Configured Kubernetes networking including ClusterIP/NodePort Services, deployed
and debugged an NGINX Ingress Controller for path-based routing across multiple
backend services, and implemented NetworkPolicies for Pod-level microsegmentation,
restricting traffic using label-based selectors to enforce least-privilege network
access."

### MODULE 2: Interview Q&A (continued)
- Q: Difference between Service and Ingress? A: Service = stable internal L4
  address + load balancing across matching Pods. Ingress = L7 HTTP routing in
  front of one or more Services, enabling path/host-based routing, TLS termination,
  multiple apps behind one entry point.
- Q: Does every cluster enforce NetworkPolicy? A: No - depends entirely on the CNI.
  Applying one against an unsupported CNI succeeds with no error but has zero effect.
  Always verify against the live cluster, not assumptions.

### MODULE 2: STATUS - COMPLETE (June 18, 2026)

## MODULE 3: Kubernetes Storage & Workloads
### Date: June 18, 2026

### Concepts Learned
- emptyDir: ephemeral volume, dies with the Pod, fine for scratch space only
- PersistentVolume (PV) + PersistentVolumeClaim (PVC): PV is the actual storage
  resource, PVC is a request/binding to it. Survives Pod deletion/recreation as
  long as PVC isn't deleted. Proved live: wrote unique data, deleted Pod, recreated
  from same YAML, data was still there.
- StorageClass: enables dynamic provisioning - PVC requests storage without a
  manually pre-created PV; the StorageClass's provisioner creates one automatically.
  kind ships a default StorageClass (local-path-provisioner) out of the box.
- StatefulSet: like Deployment but gives stable, predictable Pod names (web-0,
  web-1, web-2 instead of random suffixes) and a dedicated PVC per replica via
  volumeClaimTemplates. Required for anything stateful (databases, queues) where
  identity and storage must follow a specific replica, not be interchangeable.
- DaemonSet: runs exactly one Pod per node automatically, no replica count needed.
  Real use cases: log collectors (Fluentd/Promtail), node monitoring agents,
  CNI/networking components.
- Job: runs a Pod to completion once, then stops (no restart on success). Used for
  one-off tasks like DB migrations, batch processing.
- CronJob: runs a Job on a schedule (cron syntax). Used for backups, scheduled
  reports, cleanup tasks.

### Commands Learned
- kubectl wait --for=condition=Ready/complete pod|job/<name> --timeout=Ns
- kubectl get storageclass
- kubectl create job --from=cronjob/<name> <job-name> - manually trigger a CronJob's
  template immediately without waiting for the schedule

### MODULE 3: Practical Assignment Given
- Deploy a StatefulSet-based 2-replica "datastore" using Postgres image with PVC
  per replica, prove each replica's data survives pod deletion. [STATUS: pending]

### MODULE 3: Resume Bullet
"Implemented persistent and stateful Kubernetes workloads including PersistentVolumes/Claims
for data durability, StatefulSets for stable network identity and per-replica storage,
DaemonSets for node-level agents, and Jobs/CronJobs for batch and scheduled task execution."

### MODULE 3: Interview Q&A
- Q: Difference between Deployment and StatefulSet? A: Deployment Pods are
  interchangeable (random names, shared storage or none); StatefulSet Pods have
  stable, ordered names and each gets its own dedicated PersistentVolumeClaim -
  required for databases and anything needing consistent identity/storage.
- Q: PV vs PVC? A: PV is the actual storage resource (the "supply"); PVC is a
  request for storage matching certain criteria (the "demand"). Kubernetes binds
  a PVC to a matching PV (or dynamically provisions one via a StorageClass).
- Q: When would you use a DaemonSet over a Deployment? A: When you need exactly
  one instance per node regardless of node count - log shippers, monitoring agents,
  CNI plugins - rather than a fixed/scaled replica count.

### MODULE 3: STATUS - COMPLETE (June 18, 2026)

## MODULE 3: Kubernetes Storage & Workloads
### Date: June 18, 2026

### Concepts Learned
- emptyDir: ephemeral volume, dies with the Pod, fine for scratch space only
- PersistentVolume (PV) + PersistentVolumeClaim (PVC): PV is the actual storage
  resource, PVC is a request/binding to it. Survives Pod deletion/recreation as
  long as PVC isn't deleted. Proved live: wrote unique data, deleted Pod, recreated
  from same YAML, data was still there.
- StorageClass: enables dynamic provisioning - PVC requests storage without a
  manually pre-created PV; the StorageClass's provisioner creates one automatically.
  kind ships a default StorageClass (local-path-provisioner) out of the box.
- StatefulSet: like Deployment but gives stable, predictable Pod names (web-0,
  web-1, web-2 instead of random suffixes) and a dedicated PVC per replica via
  volumeClaimTemplates. Required for anything stateful (databases, queues) where
  identity and storage must follow a specific replica, not be interchangeable.
- DaemonSet: runs exactly one Pod per node automatically, no replica count needed.
  Real use cases: log collectors (Fluentd/Promtail), node monitoring agents,
  CNI/networking components.
- Job: runs a Pod to completion once, then stops (no restart on success). Used for
  one-off tasks like DB migrations, batch processing.
- CronJob: runs a Job on a schedule (cron syntax). Used for backups, scheduled
  reports, cleanup tasks.

### Commands Learned
- kubectl wait --for=condition=Ready/complete pod|job/<name> --timeout=Ns
- kubectl get storageclass
- kubectl create job --from=cronjob/<name> <job-name> - manually trigger a CronJob's
  template immediately without waiting for the schedule

### MODULE 3: Practical Assignment Given
- Deploy a StatefulSet-based 2-replica "datastore" using Postgres image with PVC
  per replica, prove each replica's data survives pod deletion. [STATUS: pending]

### MODULE 3: Resume Bullet
"Implemented persistent and stateful Kubernetes workloads including PersistentVolumes/Claims
for data durability, StatefulSets for stable network identity and per-replica storage,
DaemonSets for node-level agents, and Jobs/CronJobs for batch and scheduled task execution."

### MODULE 3: Interview Q&A
- Q: Difference between Deployment and StatefulSet? A: Deployment Pods are
  interchangeable (random names, shared storage or none); StatefulSet Pods have
  stable, ordered names and each gets its own dedicated PersistentVolumeClaim -
  required for databases and anything needing consistent identity/storage.
- Q: PV vs PVC? A: PV is the actual storage resource (the "supply"); PVC is a
  request for storage matching certain criteria (the "demand"). Kubernetes binds
  a PVC to a matching PV (or dynamically provisions one via a StorageClass).
- Q: When would you use a DaemonSet over a Deployment? A: When you need exactly
  one instance per node regardless of node count - log shippers, monitoring agents,
  CNI plugins - rather than a fixed/scaled replica count.

### MODULE 3: STATUS - COMPLETE (June 18, 2026)

### Major Incident: Ingress returned 504 Gateway Timeout - root cause was NetworkPolicy
**Date:** June 20, 2026

**Symptom:** curl through Ingress Controller (port-forward 8080) consistently returned 
504 Gateway Timeout, even after restarting the Ingress Controller Pod and even after 
fully recreating the kind cluster.

**Misleading clue:** kubectl port-forward directly to nginx-service (port 9090) worked 
PERFECTLY, returning the correct page. This initially pointed toward "Ingress Controller 
itself is broken" since the backend seemed healthy.

**Real diagnosis path:**
1. Checked Pods (kubectl get pods -l app=nginx) -> all Running, healthy
2. Checked Service (kubectl describe svc nginx-service) -> Endpoints listed correctly
3. Tested Service directly via port-forward (9090) -> WORKED (this was the misleading part)
4. Restarted Ingress Controller Pod -> still 504
5. Recreated entire kind cluster fresh -> still 504
6. Checked Ingress Controller's OWN LOGS (kubectl logs -n ingress-nginx -l 
   app.kubernetes.io/component=controller) -> found the real error:
   "upstream timed out while connecting to upstream http://<pod-ip>:80/"
   - tried 3 different pod IPs, ALL timed out
7. This meant: Ingress Controller could not reach ANY nginx Pod over real Pod-to-Pod 
   network traffic - but kubectl port-forward to the same Pods worked fine
8. KEY INSIGHT: kubectl port-forward tunnels through the Kubernetes API server directly 
   into the container - it does NOT go through normal CNI Pod networking, which means 
   it BYPASSES NetworkPolicy enforcement entirely. This is why port-forward gave a 
   false sense that "the Pod is reachable" when real network traffic was actually blocked.
9. Checked NetworkPolicies (kubectl get networkpolicy) -> found two policies targeting 
   app=nginx pods:
   - nginx-deny-all: blocks ALL ingress traffic to app=nginx pods by default
   - nginx-allow-labeled: only allows traffic FROM pods labeled access=true - 
     nothing else
10. The Ingress Controller Pod (in a separate ingress-nginx namespace) has neither the 
    access=true label nor any explicit allow rule -> traffic silently blocked -> 
    timeout -> 504

**Fix:** Updated nginx-allow-labeled NetworkPolicy to add a second allow rule using 
namespaceSelector, permitting traffic from any Pod in the ingress-nginx namespace 
(matched via the auto-applied kubernetes.io/metadata.name label every namespace has):

ingress:
  - from:
      - podSelector:
          matchLabels:
            access: "true"
      - namespaceSelector:
          matchLabels:
            kubernetes.io/metadata.name: ingress-nginx

After applying, curl through Ingress Controller succeeded immediately.

### Concepts Learned
- NetworkPolicy enforces actual network-level rules between Pods (Layer 3/4) - it can 
  completely block legitimate traffic even when Pods/Services/Endpoints all look healthy
- kubectl port-forward bypasses CNI networking and NetworkPolicy entirely - it is NOT 
  a reliable way to test whether "real" network traffic (like from another Pod) can 
  reach a Pod. Only useful for testing from your own machine, not for simulating 
  Pod-to-Pod connectivity.
- A "from" list in a NetworkPolicy ingress rule with multiple entries (podSelector, 
  namespaceSelector) acts as OR logic - traffic is allowed if it matches ANY listed rule
- namespaceSelector lets you allow traffic from an entire namespace, using namespace 
  labels (every namespace auto-has kubernetes.io/metadata.name=<namespace-name> by default)
- When debugging "Service/Pods look healthy but traffic still fails," check 
  NetworkPolicies - they are invisible in kubectl get pods/svc output but can silently 
  block real traffic

### Interview Q&A
Q: A Service's Endpoints show healthy Pod IPs, and kubectl port-forward to the Pod 
works, but another Pod still can't reach it. What would you check?
A: NetworkPolicies. kubectl port-forward bypasses normal CNI networking by tunneling 
through the API server directly into the container, so it doesn't respect 
NetworkPolicy rules. Real Pod-to-Pod traffic, like from an Ingress Controller, does 
respect NetworkPolicy - so a restrictive policy can silently block legitimate traffic 
while still appearing "healthy" via port-forward tests.

Q: How do you allow traffic from an entire namespace (e.g., an Ingress Controller 
namespace) in a NetworkPolicy?
A: Use a namespaceSelector in the ingress.from rule, matching against namespace labels - 
commonly kubernetes.io/metadata.name, which Kubernetes automatically sets to the 
namespace's own name on every namespace.

### MODULE 2: STATUS - Ingress fully verified working end-to-end (after major 
NetworkPolicy debugging session)


## MODULE 3: Kubernetes Storage & Workloads
### Date: July 9, 2026

### PV Persistence Test — VERIFIED WORKING
- Wrote "PERSISTENT-DATA-XYZ" to /data/file.txt inside pv-test-pod
- Deleted the Pod entirely
- Recreated Pod from same YAML (same PVC claim)
- Data was still there — proves PV survives Pod deletion

### All Objects Verified Healthy on Fresh Cluster
- StatefulSet web: 3/3 Running (web-0, web-1, web-2) each with own PVC
- DaemonSet node-monitor: 1/1 (one per node, as expected)
- Job db-migration-job: Completed
- CronJob backup-cronjob: firing automatically every 5 min, self-resumed after 19-day gap

### MODULE 3: STATUS - COMPLETE

## MODULE 4: Docker Deep Dive
### Date: July 10, 2026

### What I Built
- FastAPI app with /health, /, /items, /db-check endpoints
- /metrics endpoint auto-instrumented with prometheus-fastapi-instrumentator
- Production-grade multi-stage Dockerfile:
  - Stage 1 (builder): installs pip dependencies only
  - Stage 2 (production): copies only installed packages, runs as non-root user
- Built image: devsecops-api:v1.0.0
- Pushed to Docker Hub: shambhavi004/devsecops-api:v1.0.0

### Key Concepts
- Multi-stage builds: separate build environment from runtime, smaller/cleaner final image
- Non-root user: security best practice, never run containers as root in production
- Layer caching: COPY requirements.txt + pip install BEFORE copying app code,
  so code changes don't invalidate the dependency cache layer
- HEALTHCHECK: built into image, Kubernetes uses this for liveness/readiness probes

### MODULE 4: STATUS - COMPLETE

## Module 5: Helm ✅
- Installed Helm v3.21.2 (no-sudo method via ~/.local/bin)
- Created chart: helm/devsecops-api/ with Chart.yaml, values.yaml, templates/
- helm install devsecops helm/devsecops-api/ → 2 pods running, ClusterIP service
- Tested: curl localhost:8002/health → {"status":"healthy","version":"1.0.0"}
- Key concept: values.yaml = settings panel, templates = parameterized K8s YAML

## Module 6: Terraform ✅
- Installed Terraform v1.9.8 (no-sudo method)
- Created terraform/kind-cluster/ with main.tf, variables.tf, outputs.tf
- terraform init → downloaded tehcyx/kind provider v0.2.0
- terraform plan → showed 1 resource to create
- terraform apply → created kind cluster "devsecops-platform-tf" in 2m29s
- terraform state list → kind_cluster.devsecops tracked in state
- terraform destroy → deleted cluster cleanly
- Key concept: IaC = infrastructure reproducible from code, full lifecycle management

## Module 7: GitHub Actions CI ✅
- Created .github/workflows/ci.yml
- Triggers on every push to main
- Builds Docker image with root context, Dockerfile in ./docker/
- Pushes to DockerHub as shambhavi004/devsecops-api:<git-sha>
- Secrets: DOCKERHUB_USERNAME, DOCKERHUB_TOKEN stored in GitHub Actions secrets
- Key concept: CI = every push automatically tested and built, no manual docker build needed

## Module 8: DevSecOps Tools ✅
- Gitleaks: scans git history for leaked secrets
- Checkov: scans Terraform/K8s YAML for misconfigurations (soft_fail=true)
- Trivy: scans Docker image for CRITICAL/HIGH CVEs
- Pipeline order: gitleaks → build-and-push → trivy (checkov runs in parallel)
- Key concept: shift-left security = catch vulnerabilities before production

## Module 9: ArgoCD & GitOps ✅
- Installed ArgoCD v3.4.5 in argocd namespace
- Created gitops/argocd-app.yaml pointing to helm/devsecops-api on GitHub
- ArgoCD auto-synced and deployed 2 pods from GitHub → cluster
- syncPolicy: automated with prune=true, selfHeal=true
- Key concept: GitOps = Git is single source of truth, ArgoCD reconciles cluster state
