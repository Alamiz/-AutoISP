"use client"

import * as React from "react"
import {
  AudioWaveform,
  BarChart3,
  BookOpen,
  Bot,
  Command,
  Frame,
  GalleryVerticalEnd,
  Home,
  Map,
  PieChart,
  Settings2,
  SquareTerminal,
  User,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { cn } from "@/lib/utils"
import { NavProjects } from "@/components/nav-projects"
import { NavUser } from "@/components/nav-user"
import { ProviderSwitcher } from "@/components/provider-switcher"
import { SettingsDialog } from "@/components/settings-dialog"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import { Separator } from "./ui/separator"

// Custom logo components
const GmxLogo = ({ className }: { className?: string }) => (
  <div className={cn("flex items-center justify-center font-bold text-[0.6rem]", className)}>GM</div>
)

const WebdeLogo = ({ className }: { className?: string }) => (
  <div className={cn("flex items-center justify-center font-bold text-[0.6rem]", className)}>WE</div>
)

// This is sample data.
const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  providers: [
    {
      name: "GMX",
      slug: "gmx",
      logo: GmxLogo,
      plan: "Provider",
    },
    {
      name: "Web.de",
      slug: "webde",
      logo: WebdeLogo,
      plan: "Provider",
    },
  ],
  navMain: [
    {
      title: "Home",
      url: "/",
      icon: Home,
    },
    // {
    //   title: "Dashboard",
    //   url: "/dashboard",
    //   icon: BarChart3,
    // },
    // {
    //   title: "Accounts",
    //   url: "/accounts",
    //   icon: User,
    // },
    // {
    //   title: "Automations",
    //   url: "/automations",
    //   icon: Bot,
    // },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const [openSettings, setOpenSettings] = React.useState(false)

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader className="pt-10">
        <ProviderSwitcher providers={data.providers} />
      </SidebarHeader>
      <Separator />
      <SidebarContent>
        <NavMain items={data.navMain} label="Platform" />
        {/* <NavProjects projects={data.projects} /> */}
      </SidebarContent>
      <Separator />
      <SidebarFooter>
        {/* <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              size="lg"
              tooltip="Settings"
              onClick={() => setOpenSettings(true)}
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground cursor-pointer"
            >
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                <Settings2 className="size-4" />
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">Settings</span>
                <span className="truncate text-xs">Account & Preferences</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu> */}
        <NavUser />
      </SidebarFooter>
      <SidebarRail />
      <SettingsDialog open={openSettings} onOpenChange={setOpenSettings} />
    </Sidebar>
  )
}
