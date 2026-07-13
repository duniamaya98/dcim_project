---
title: Service Discovery Comparison
created: 2026-06-23
updated: 2026-06-23
type: comparison
tags: [comparison, architecture]
sources: []
confidence: medium
---

# Service Discovery Comparison

Perbandingan service discovery solutions.

## Consul
- **Type**: Service discovery + configuration
- **Strengths**: Service mesh, KV store, health checks
- **Weaknesses**: Complex setup, HashiCorp ecosystem
- **Best for**: HashiCorp stack, service mesh

## etcd
- **Type**: Distributed key-value store
- **Strengths**: Simple, reliable, Kubernetes-native
- **Weaknesses**: Limited features vs Consul
- **Best for**: Kubernetes, simple discovery

## Eureka (Netflix)
- **Type**: Service discovery
- **Strengths**: Spring ecosystem, simple
- **Weaknesses**: Limited features, Netflix maintenance
- **Best for**: Spring Boot applications

## Kubernetes DNS
- **Type**: Built-in K8s service discovery
- **Strengths**: Native, simple, automatic
- **Weaknesses**: K8s only, limited features
- **Best for**: Kubernetes environments

## Comparison Matrix

| Feature | Consul | etcd | Eureka | K8s DNS |
|---------|--------|------|--------|---------|
| Health Checks | Yes | Limited | Yes | Yes |
| KV Store | Yes | Yes | No | No |
| Service Mesh | Yes | No | No | No |
| Ease of Setup | Medium | Low | Low | Low |
| Scalability | High | High | Medium | High |

## Recommendation
- **Consul**: For HashiCorp stack, advanced features
- **Kubernetes DNS**: For K8s environments
- **etcd**: For simple, Kubernetes-native

## Related
- [[infrastructure-provisioning]]
- [[kubernetes]]
- [[dcim-core-platform]]
