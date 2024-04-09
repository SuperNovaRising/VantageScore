# Summary
This is a self-contained codebase which provides postgres database for generic use. It leverages [helm chart](https://helm.sh/) to simply the cluster creation.

The `users` table is instantiated with 2 users, each with user name and hashed password (encrypted by bcrypt):
`admin`, `password`
`other`, `nosecret`

`admin` user has the privilege to read, create, update and delete items in `employee` resource
`other` user has the privilege to read items in `employee` resource

# Install postgres helm chart
You may need to install `helm` in advance.

```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install my-postgres bitnami/postgresql -f custom.yaml
```

# Spin up Kubernetes cluster locally
## Use k9s to examine the pod and instances
```
k9s
```
## Expose the application to port 5432
```
kubectl port-forward svc/my-postgres-postgresql 5432:5432
```

## Connect to the local postgres database
In another terminal:
```
export POSTGRES_PASSWORD=$(kubectl get secret --namespace default my-postgres-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)

PGPASSWORD="$POSTGRES_PASSWORD" psql --host 127.0.0.1 -U root  -d postgres -p 5432
```


## Clean up
Due to the [issue](https://github.com/bitnami/charts/issues/15975), bitnami `uninstall` command cannot clean up the pvc (persistent volume claim) and pv (persistent volume) automatically, manually cleanup is required.

Terminate the port forwarding.

```
helm uninstall my-postgres
kubectl delete pvc --all 
kubectl delete pv --all
```
Use `helm`, `k9s` and `kubectl` to examine the resources to be cleaned
```
helm list
k9s
kubectl get svc
kubectl get pods
kubectl get pvc
kubectl get pv
```