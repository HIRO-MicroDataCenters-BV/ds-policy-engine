# Deploy — cog-engine dev cluster

Per-cluster deployment config for the **cognitive-engine** cluster (RKE2 + Calico, Juju/Rancher-managed).

The nextgen sites (ki/hus/uva) are deployed from the [`ds-gitops`](https://github.com/HIRO-MicroDataCenters-BV) repo via Fleet. The cog cluster has **no GitOps values repo**, so its values live here (`values.yaml`) and are applied with a direct `helm install`. The image is **public on GHCR**, so no pull secret is required.

## 1. Deploy

```bash
kubectl config use-context cognitive-engine

helm install ds-policy-engine ../../server/charts/ds-policy-engine \
  -n policy-engine --create-namespace \
  -f values.yaml

kubectl -n policy-engine rollout status deploy/ds-policy-engine --timeout=150s
```

## 2. Seed the tier rules

```bash
kubectl -n policy-engine port-forward svc/ds-policy-engine 8000:8000 &   # localhost:8000 -> in-cluster svc

for r in \
  '{"name":"Free Tier","role":"free_tier","institute":"cogapi","permissions":["model:read","model:upload","dataset:read","pipeline:read"],"enabled":true}' \
  '{"name":"Enterprise Tier","role":"enterprise_tier","institute":"cogapi","permissions":["model:read","model:create","model:upload","model:serve","model:fine-tune","dataset:read","dataset:create","pipeline:read","pipeline:create","pipeline:run"],"enabled":true}' \
  '{"name":"Admin Tier","role":"admin_tier","institute":"cogapi","permissions":["model:read","model:create","model:upload","model:serve","model:fine-tune","dataset:read","dataset:create","pipeline:read","pipeline:create","pipeline:run"],"enabled":true}' ; do
  curl -s -X POST localhost:8000/api/v1/rules -H 'content-type: application/json' -d "$r"
done
curl -s -X POST localhost:8000/api/v1/policies/deploy -H 'content-type: application/json' -d '{"deployed_by":"cog-setup"}'
curl -s localhost:8000/api/v1/decision-matrix | python3 -m json.tool   # free=4, enterprise=10, admin=10
kill %1
```

## 3. Point Cog-Engine at it

Set on the cog-api app (charm config, or the `policy_engine_base_url` default in Cog-Engine + redeploy):

```
POLICY_ENGINE_BASE_URL=http://ds-policy-engine.policy-engine.svc.cluster.local:8000
```

Verify: `GET /cogapi/entitlements` for an enterprise user returns `tier: enterprise` with no `entitlement.pdp_unavailable` in the cog-api logs.

## 4. Lock it down

Calico enforces NetworkPolicy on this cluster. Restrict ingress to the cog-api pod only (default-deny for every other pod, since the policy engine has no auth of its own):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ds-policy-engine-allow-cogapi
  namespace: policy-engine
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: ds-policy-engine
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kubeflow
          podSelector:
            matchLabels:
              app.kubernetes.io/name: cog-api        # verify: kubectl -n kubeflow get pod cog-api-dev-0 --show-labels
      ports:
        - protocol: TCP
          port: 8000
```

## Rollback

```bash
helm uninstall ds-policy-engine -n policy-engine
kubectl delete networkpolicy ds-policy-engine-allow-cogapi -n policy-engine
```

Revert `POLICY_ENGINE_BASE_URL` to the nextgen URL. Cog-Engine fails **open**, so nothing breaks live traffic during rollback.
