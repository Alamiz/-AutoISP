import { ChevronRight, LucideIcon } from "lucide-react"
import { SidebarGroup, SidebarGroupLabel, SidebarMenu, SidebarMenuItem, SidebarMenuButton, SidebarMenuSub, SidebarMenuSubButton, SidebarMenuSubItem } from "./ui/sidebar"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@radix-ui/react-collapsible"
import clsx from "clsx"
import { usePathname } from "next/navigation"
import Link from "next/link"

export function NavMain({
  items,
  label,
}: {
  items: {
    title: string
    url: string
    icon?: LucideIcon
    isActive?: boolean
    items?: {
      title: string
      url: string
    }[]
  }[]
  label?: string
}) {
  const currentPathName = usePathname();

  return (
    <SidebarGroup>
      {label && <SidebarGroupLabel>{label}</SidebarGroupLabel>}
      <SidebarMenu>
        {items.map((item) => {
          const normalize = (path: string) => path.endsWith('/') ? path : `${path}/`;
          const activePath = normalize(currentPathName);
          const itemPath = normalize(item.url);

          const isCurrentPathActive = activePath === itemPath;
          const isAnySubItemActive = item.items?.some(subItem => normalize(subItem.url) === activePath);
          const isGroupActive = item.isActive || isAnySubItemActive;

          if (!item.items?.length) {
            return (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton
                  asChild
                  tooltip={item.title}
                  isActive={isCurrentPathActive}
                  className={clsx(
                    {
                      "text-foreground bg-accent/50 border-r-2 border-primary": isCurrentPathActive,
                      "text-muted-foreground hover:text-foreground": !isCurrentPathActive,
                    },
                    "font-semibold transition-all duration-200"
                  )}
                >
                  <Link href={item.url}>
                    {item.icon && <item.icon />}
                    <span>{item.title}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            )
          }
          return (
            <Collapsible
              key={item.title}
              asChild
              defaultOpen={isGroupActive}
              className="group/collapsible"
            >
              <SidebarMenuItem>
                <CollapsibleTrigger asChild>
                  <SidebarMenuButton
                    tooltip={item.title}
                    className={clsx(
                      {
                        "font-semibold text-foreground": isGroupActive,
                        "text-muted-foreground": !isGroupActive,
                      }
                    )}
                  >
                    {item.icon && <item.icon />}
                    <span>{item.title}</span>
                    <ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                  </SidebarMenuButton>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <SidebarMenuSub>
                    {item.items?.map((subItem) => {
                      const isSubItemActive = currentPathName === subItem.url;
                      return (
                        <SidebarMenuSubItem key={subItem.title}>
                          <SidebarMenuSubButton
                            asChild
                            isActive={isSubItemActive}
                            className={clsx(
                              {
                                "font-semibold text-foreground bg-accent/30": isSubItemActive,
                                "text-muted-foreground hover:text-foreground": !isSubItemActive,
                              },
                              "transition-all duration-200"
                            )}
                          >
                            <Link href={subItem.url}>
                              <span>{subItem.title}</span>
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      )
                    })}
                  </SidebarMenuSub>
                </CollapsibleContent>
              </SidebarMenuItem>
            </Collapsible>
          )
        })}
      </SidebarMenu>
    </SidebarGroup>
  )
}
