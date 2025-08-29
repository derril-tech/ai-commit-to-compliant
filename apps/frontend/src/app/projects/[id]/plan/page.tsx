'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import {
  Container,
  Title,
  Text,
  Card,
  Group,
  Badge,
  Button,
  Stack,
  Grid,
  Tabs,
  Alert,
  Progress,
  List,
  ThemeIcon,
  ActionIcon,
  Tooltip,
  Modal,
  Textarea,
} from '@mantine/core';
import {
  IconCheck,
  IconX,
  IconAlertTriangle,
  IconInfoCircle,
  IconDollarSign,
  IconCode,
  IconShield,
  IconGauge,
  IconExternalLink,
  IconEye,
} from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { AppShell } from '@/components/AppShell';
import { useBlueprint, api } from '@/lib/api';

export default function PlanPreviewPage() {
  const params = useParams();
  const projectId = params.id as string;
  const { blueprint, isLoading, mutate } = useBlueprint(projectId);
  const [approving, setApproving] = useState(false);
  const [waiveModalOpened, { open: openWaiveModal, close: closeWaiveModal }] = useDisclosure(false);
  const [selectedPolicy, setSelectedPolicy] = useState<any>(null);
  const [waiveReason, setWaiveReason] = useState('');

  if (isLoading) {
    return (
      <AppShell>
        <Container size="xl">
          <Text>Loading plan...</Text>
        </Container>
      </AppShell>
    );
  }

  if (!blueprint) {
    return (
      <AppShell>
        <Container size="xl">
          <Alert icon={<IconAlertTriangle size={16} />} color="yellow">
            No plan available. Please run the audit first.
          </Alert>
        </Container>
      </AppShell>
    );
  }

  const handleApprove = async () => {
    try {
      setApproving(true);
      await api.post('/pipelines/apply', { project_id: projectId });
      notifications.show({
        title: 'Plan Approved',
        message: 'Infrastructure provisioning has started',
        color: 'green',
      });
      mutate();
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to approve plan',
        color: 'red',
      });
    } finally {
      setApproving(false);
    }
  };

  const handleWaivePolicy = async () => {
    try {
      await api.post(`/policies/waive`, {
        project_id: projectId,
        policy_name: selectedPolicy.name,
        reason: waiveReason,
      });
      notifications.show({
        title: 'Policy Waived',
        message: `${selectedPolicy.name} has been waived`,
        color: 'blue',
      });
      closeWaiveModal();
      setWaiveReason('');
      mutate();
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to waive policy',
        color: 'red',
      });
    }
  };

  const failedPolicies = blueprint.policies.filter((p: any) => !p.enabled && p.name !== 'test_coverage');
  const canApprove = failedPolicies.length === 0;

  return (
    <AppShell>
      <Container size="xl">
        <Group justify="space-between" mb="xl">
          <div>
            <Title order={1}>Deployment Plan</Title>
            <Text c="dimmed">Review infrastructure, CI/CD, and policy configuration</Text>
          </div>
          <Group>
            <Button
              variant="outline"
              leftSection={<IconEye size={16} />}
              onClick={() => window.open(`/projects/${projectId}/plan/diff`, '_blank')}
            >
              View Diff
            </Button>
            <Button
              leftSection={<IconCheck size={16} />}
              disabled={!canApprove}
              loading={approving}
              onClick={handleApprove}
            >
              Approve & Deploy
            </Button>
          </Group>
        </Group>

        {!canApprove && (
          <Alert icon={<IconAlertTriangle size={16} />} color="red" mb="xl">
            <Text fw={500}>Deployment Blocked</Text>
            <Text size="sm">
              {failedPolicies.length} policy gate(s) must be resolved or waived before deployment.
            </Text>
          </Alert>
        )}

        <Tabs defaultValue="overview">
          <Tabs.List>
            <Tabs.Tab value="overview" leftSection={<IconInfoCircle size={16} />}>
              Overview
            </Tabs.Tab>
            <Tabs.Tab value="infrastructure" leftSection={<IconCode size={16} />}>
              Infrastructure
            </Tabs.Tab>
            <Tabs.Tab value="policies" leftSection={<IconShield size={16} />}>
              Policy Gates
            </Tabs.Tab>
            <Tabs.Tab value="cost" leftSection={<IconDollarSign size={16} />}>
              Cost Estimate
            </Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="overview" pt="md">
            <Grid>
              <Grid.Col span={{ base: 12, md: 8 }}>
                <Card withBorder>
                  <Title order={3} mb="md">Plan Summary</Title>
                  <Stack gap="md">
                    <Group justify="space-between">
                      <Text>Resources to create:</Text>
                      <Badge color="green">{blueprint.plan_diff.resources_to_create}</Badge>
                    </Group>
                    <Group justify="space-between">
                      <Text>Workflows to create:</Text>
                      <Badge color="blue">{blueprint.plan_diff.workflows_to_create}</Badge>
                    </Group>
                    <Group justify="space-between">
                      <Text>Estimated apply time:</Text>
                      <Text>{blueprint.plan_diff.estimated_apply_time_minutes} minutes</Text>
                    </Group>
                    <Group justify="space-between">
                      <Text>Monthly cost estimate:</Text>
                      <Text fw={500}>${blueprint.cost_estimate.monthly_estimate}</Text>
                    </Group>
                  </Stack>
                </Card>
              </Grid.Col>

              <Grid.Col span={{ base: 12, md: 4 }}>
                <Card withBorder>
                  <Title order={3} mb="md">Policy Status</Title>
                  <Stack gap="xs">
                    {blueprint.policies.map((policy: any) => (
                      <Group key={policy.name} justify="space-between">
                        <Text size="sm">{policy.name.replace('_', ' ')}</Text>
                        <ThemeIcon
                          size="sm"
                          color={policy.enabled ? 'green' : 'red'}
                          variant="light"
                        >
                          {policy.enabled ? <IconCheck size={12} /> : <IconX size={12} />}
                        </ThemeIcon>
                      </Group>
                    ))}
                  </Stack>
                </Card>
              </Grid.Col>
            </Grid>
          </Tabs.Panel>

          <Tabs.Panel value="infrastructure" pt="md">
            <Card withBorder>
              <Title order={3} mb="md">Infrastructure Resources</Title>
              <Text c="dimmed" mb="md">
                {blueprint.plan_diff.preview}
              </Text>
              
              <List spacing="sm">
                {blueprint.plan_diff.changes.map((change: any, index: number) => (
                  <List.Item
                    key={index}
                    icon={
                      <ThemeIcon color="green" size={20} radius="xl">
                        <IconCheck size={12} />
                      </ThemeIcon>
                    }
                  >
                    <Group justify="space-between">
                      <div>
                        <Text fw={500}>{change.resource_type}.{change.resource_name}</Text>
                        <Text size="sm" c="dimmed">{change.description}</Text>
                      </div>
                      <Badge color="green" variant="light">
                        {change.type}
                      </Badge>
                    </Group>
                  </List.Item>
                ))}
              </List>
            </Card>
          </Tabs.Panel>

          <Tabs.Panel value="policies" pt="md">
            <Stack gap="md">
              {blueprint.policies.map((policy: any) => (
                <Card key={policy.name} withBorder>
                  <Group justify="space-between" mb="md">
                    <div>
                      <Group gap="xs">
                        <Text fw={500}>{policy.name.replace('_', ' ')}</Text>
                        <Badge
                          color={policy.enabled ? 'green' : 'red'}
                          variant="light"
                        >
                          {policy.enabled ? 'Passed' : 'Failed'}
                        </Badge>
                      </Group>
                      <Text size="sm" c="dimmed">{policy.description}</Text>
                    </div>
                    <Group>
                      {policy.remediation_url && (
                        <Tooltip label="View documentation">
                          <ActionIcon
                            variant="subtle"
                            onClick={() => window.open(policy.remediation_url, '_blank')}
                          >
                            <IconExternalLink size={16} />
                          </ActionIcon>
                        </Tooltip>
                      )}
                      {!policy.enabled && policy.waivable && (
                        <Button
                          size="xs"
                          variant="outline"
                          onClick={() => {
                            setSelectedPolicy(policy);
                            openWaiveModal();
                          }}
                        >
                          Waive
                        </Button>
                      )}
                    </Group>
                  </Group>

                  {policy.threshold && (
                    <Stack gap="xs">
                      {Object.entries(policy.threshold).map(([key, value]) => (
                        <Group key={key} justify="space-between">
                          <Text size="sm">{key.replace('_', ' ')}:</Text>
                          <Text size="sm" fw={500}>{String(value)}</Text>
                        </Group>
                      ))}
                    </Stack>
                  )}
                </Card>
              ))}
            </Stack>
          </Tabs.Panel>

          <Tabs.Panel value="cost" pt="md">
            <Grid>
              <Grid.Col span={{ base: 12, md: 8 }}>
                <Card withBorder>
                  <Title order={3} mb="md">Monthly Cost Breakdown</Title>
                  <Stack gap="md">
                    {Object.entries(blueprint.cost_estimate.breakdown).map(([category, cost]) => (
                      <div key={category}>
                        <Group justify="space-between" mb="xs">
                          <Text tt="capitalize">{category}</Text>
                          <Text fw={500}>${Number(cost).toFixed(2)}</Text>
                        </Group>
                        <Progress
                          value={(Number(cost) / blueprint.cost_estimate.monthly_estimate) * 100}
                          size="sm"
                        />
                      </div>
                    ))}
                    <Group justify="space-between" pt="md" style={{ borderTop: '1px solid var(--mantine-color-gray-3)' }}>
                      <Text fw={500}>Total Monthly Estimate</Text>
                      <Text fw={700} size="lg">${blueprint.cost_estimate.monthly_estimate}</Text>
                    </Group>
                  </Stack>
                </Card>
              </Grid.Col>

              <Grid.Col span={{ base: 12, md: 4 }}>
                <Card withBorder>
                  <Title order={4} mb="md">Cost Optimization Tips</Title>
                  <List size="sm" spacing="xs">
                    {blueprint.cost_estimate.cost_optimization_tips.map((tip: string, index: number) => (
                      <List.Item key={index}>{tip}</List.Item>
                    ))}
                  </List>
                </Card>
              </Grid.Col>
            </Grid>
          </Tabs.Panel>
        </Tabs>

        <Modal
          opened={waiveModalOpened}
          onClose={closeWaiveModal}
          title={`Waive Policy: ${selectedPolicy?.name}`}
        >
          <Stack gap="md">
            <Text size="sm">
              Provide a reason for waiving this policy gate. This action will be logged for audit purposes.
            </Text>
            <Textarea
              label="Reason for waiving"
              placeholder="Explain why this policy should be waived..."
              value={waiveReason}
              onChange={(e) => setWaiveReason(e.target.value)}
              minRows={3}
              required
            />
            <Group justify="flex-end">
              <Button variant="outline" onClick={closeWaiveModal}>
                Cancel
              </Button>
              <Button
                onClick={handleWaivePolicy}
                disabled={!waiveReason.trim()}
              >
                Waive Policy
              </Button>
            </Group>
          </Stack>
        </Modal>
      </Container>
    </AppShell>
  );
}
