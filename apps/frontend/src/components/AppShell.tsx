'use client';

import { ReactNode } from 'react';
import {
  AppShell as MantineAppShell,
  Burger,
  Group,
  Text,
  NavLink,
  Avatar,
  Menu,
  UnstyledButton,
  rem,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import {
  IconDashboard,
  IconRocket,
  IconSettings,
  IconLogout,
  IconChevronDown,
} from '@tabler/icons-react';
import { useAuth } from '@/lib/auth';
import { useRouter, usePathname } from 'next/navigation';

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [opened, { toggle }] = useDisclosure();
  const { user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const navigation = [
    { label: 'Dashboard', icon: IconDashboard, href: '/dashboard' },
    { label: 'Projects', icon: IconRocket, href: '/projects' },
    { label: 'Settings', icon: IconSettings, href: '/settings' },
  ];

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  return (
    <MantineAppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <MantineAppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <Group gap="xs">
              <IconRocket size={24} color="blue" />
              <Text fw={700} size="lg">
                ProdSprints AI
              </Text>
            </Group>
          </Group>

          {user && (
            <Menu shadow="md" width={200}>
              <Menu.Target>
                <UnstyledButton>
                  <Group gap="xs">
                    <Avatar size="sm" radius="xl">
                      {user.name.charAt(0).toUpperCase()}
                    </Avatar>
                    <div style={{ flex: 1 }}>
                      <Text size="sm" fw={500}>
                        {user.name}
                      </Text>
                      <Text size="xs" c="dimmed">
                        {user.email}
                      </Text>
                    </div>
                    <IconChevronDown size={rem(14)} />
                  </Group>
                </UnstyledButton>
              </Menu.Target>

              <Menu.Dropdown>
                <Menu.Item
                  leftSection={<IconSettings size={rem(14)} />}
                  onClick={() => router.push('/settings')}
                >
                  Settings
                </Menu.Item>
                <Menu.Divider />
                <Menu.Item
                  leftSection={<IconLogout size={rem(14)} />}
                  onClick={handleLogout}
                >
                  Sign out
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          )}
        </Group>
      </MantineAppShell.Header>

      <MantineAppShell.Navbar p="md">
        <MantineAppShell.Section grow>
          {navigation.map((item) => (
            <NavLink
              key={item.href}
              href={item.href}
              label={item.label}
              leftSection={<item.icon size="1rem" />}
              active={pathname === item.href}
              onClick={() => router.push(item.href)}
            />
          ))}
        </MantineAppShell.Section>
      </MantineAppShell.Navbar>

      <MantineAppShell.Main>{children}</MantineAppShell.Main>
    </MantineAppShell>
  );
}
