'use client';

import { Container, Title, Text, Button, Stack, Group } from '@mantine/core';
import { IconRocket, IconShield, IconChartLine } from '@tabler/icons-react';
import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const { user, login } = useAuth();
  const router = useRouter();

  if (user) {
    router.push('/dashboard');
    return null;
  }

  return (
    <Container size="md" py={80}>
      <Stack align="center" gap="xl">
        <IconRocket size={64} color="blue" />
        
        <Stack align="center" gap="md">
          <Title order={1} ta="center">
            ProdSprints AI
          </Title>
          <Text size="xl" ta="center" c="dimmed">
            Multi-tenant release orchestrator with policy gates
          </Text>
        </Stack>

        <Group justify="center" gap="xl" mt="xl">
          <Stack align="center" gap="xs">
            <IconRocket size={32} />
            <Text fw={500}>Fast Deployments</Text>
            <Text size="sm" c="dimmed" ta="center">
              Repo to production in 20 minutes
            </Text>
          </Stack>
          
          <Stack align="center" gap="xs">
            <IconShield size={32} />
            <Text fw={500}>Policy Gates</Text>
            <Text size="sm" c="dimmed" ta="center">
              Security, tests, and compliance
            </Text>
          </Stack>
          
          <Stack align="center" gap="xs">
            <IconChartLine size={32} />
            <Text fw={500}>Observability</Text>
            <Text size="sm" c="dimmed" ta="center">
              SLOs, metrics, and dashboards
            </Text>
          </Stack>
        </Group>

        <Group mt="xl">
          <Button 
            size="lg" 
            leftSection={<IconRocket size={20} />}
            onClick={() => login('github')}
          >
            Sign in with GitHub
          </Button>
          <Button 
            size="lg" 
            variant="outline"
            onClick={() => login('google')}
          >
            Sign in with Google
          </Button>
        </Group>
      </Stack>
    </Container>
  );
}
