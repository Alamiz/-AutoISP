"use client"

import * as React from "react"
import {
    ColumnDef,
    ColumnFiltersState,
    SortingState,
    VisibilityState,
    flexRender,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable,
} from "@tanstack/react-table"
import { cn } from "@/lib/utils"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Trash2, Download, Settings2, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Filter } from "lucide-react"

interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[]
    data: TData[]
    filterColumn?: string
    filterPlaceholder?: string
    onDeleteSelected?: (selectedRows: TData[]) => void
    onExportSelected?: (selectedRows: TData[]) => void
    actions?: (selectedRows: TData[]) => React.ReactNode
    enableRowSelectionOnClick?: boolean
    totalCount?: number
    onSelectAllItems?: () => void
    onClearSelection?: () => void
    selectedCount?: number
    rowSelection?: Record<string, boolean>
    onRowSelectionChange?: (updaterOrValue: any) => void
    getRowId?: (row: TData) => string
    statusFilter?: {
        options: { label: string, value: string }[]
        value: string
        onChange: (value: string) => void
    }
    showTopSelectionCount?: boolean
    showViewDropdown?: boolean
    className?: string
    containerClassName?: string
    hidePagination?: boolean
    hideBanners?: boolean
    hideBorder?: boolean
    hideRounding?: boolean
}

export function DataTable<TData, TValue>({
    columns,
    data,
    filterColumn,
    filterPlaceholder = "Filter...",
    onDeleteSelected,
    onExportSelected,
    actions,
    enableRowSelectionOnClick,
    totalCount,
    onSelectAllItems,
    onClearSelection,
    selectedCount,
    rowSelection: externalRowSelection,
    onRowSelectionChange: onExternalRowSelectionChange,
    getRowId,
    statusFilter,
    showTopSelectionCount = true,
    showViewDropdown = true,
    className,
    containerClassName,
    hidePagination = false,
    hideBanners = false,
    hideBorder = false,
    hideRounding = false,
}: DataTableProps<TData, TValue>) {
    const [sorting, setSorting] = React.useState<SortingState>([])
    const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
    const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
    const [internalRowSelection, setInternalRowSelection] = React.useState({})

    const rowSelection = externalRowSelection || internalRowSelection
    const onRowSelectionChange = onExternalRowSelectionChange || setInternalRowSelection

    const table = useReactTable({
        data,
        columns,
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        onColumnVisibilityChange: setColumnVisibility,
        onRowSelectionChange,
        getRowId: getRowId || ((row: any) => row.id),
        initialState: {
            pagination: {
                pageSize: hidePagination ? 1000 : 10,
            },
        },
        state: {
            sorting,
            columnFilters,
            columnVisibility,
            rowSelection,
        },
    })

    const selectedRows = table.getFilteredSelectedRowModel().rows.map((row) => row.original)

    const hasTopActions = !!(filterColumn || (selectedRows.length > 0 && (showTopSelectionCount || onExportSelected || actions || onDeleteSelected)) || statusFilter || showViewDropdown)
    const hasSelectAllBanner = !hideBanners && table.getIsAllPageRowsSelected() && totalCount && totalCount > table.getRowModel().rows.length && (selectedCount ?? selectedRows.length) < totalCount
    const hasAllSelectedBanner = !hideBanners && totalCount && (selectedCount ?? selectedRows.length) === totalCount && totalCount > 0

    return (
        <div className={cn("flex flex-col", className)}>
            {hasTopActions && (
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2 flex-1">
                        {filterColumn && (
                            <Input
                                placeholder={filterPlaceholder}
                                value={(table.getColumn(filterColumn)?.getFilterValue() as string) ?? ""}
                                onChange={(event) =>
                                    table.getColumn(filterColumn)?.setFilterValue(event.target.value)
                                }
                                className="max-w-sm"
                            />
                        )}

                        {selectedRows.length > 0 && (
                            <div className="flex items-center gap-2 animate-in fade-in slide-in-from-left-2 duration-300">
                                {showTopSelectionCount && (
                                    <span className="text-sm text-muted-foreground mr-2">
                                        {selectedCount ?? selectedRows.length} selected
                                    </span>
                                )}
                                {onExportSelected && (
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => onExportSelected(selectedRows)}
                                    >
                                        <Download className="mr-2 h-4 w-4" />
                                        Export
                                    </Button>
                                )}
                                {actions && actions(selectedRows)}
                                {onDeleteSelected && (
                                    <AlertDialog>
                                        <AlertDialogTrigger asChild>
                                            <Button variant="destructive" size="sm">
                                                <Trash2 className="mr-2 h-4 w-4" />
                                                Delete
                                            </Button>
                                        </AlertDialogTrigger>
                                        <AlertDialogContent>
                                            <AlertDialogHeader>
                                                <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                                                <AlertDialogDescription>
                                                    This action cannot be undone. This will permanently delete {selectedRows.length} selected items from the database.
                                                </AlertDialogDescription>
                                            </AlertDialogHeader>
                                            <AlertDialogFooter>
                                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                                <AlertDialogAction
                                                    onClick={() => {
                                                        onDeleteSelected(selectedRows)
                                                        table.resetRowSelection()
                                                    }}
                                                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                                >
                                                    Delete
                                                </AlertDialogAction>
                                            </AlertDialogFooter>
                                        </AlertDialogContent>
                                    </AlertDialog>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="flex items-center gap-2">
                        {statusFilter && (
                            <Select value={statusFilter.value || "all"} onValueChange={statusFilter.onChange}>
                                <SelectTrigger className="w-[150px] h-8 text-xs border-border bg-card">
                                    <div className="flex items-center gap-2">
                                        <Filter className="h-3.5 w-3.5 text-muted-foreground" />
                                        <SelectValue placeholder="Filter Status" />
                                    </div>
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Statuses</SelectItem>
                                    {statusFilter.options.map((opt) => (
                                        <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        )}

                        {showViewDropdown && (
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="outline" size="sm" className="ml-auto">
                                        <Settings2 className="mr-2 h-4 w-4" />
                                        View
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                    {table
                                        .getAllColumns()
                                        .filter((column) => column.getCanHide())
                                        .map((column) => {
                                            return (
                                                <DropdownMenuCheckboxItem
                                                    key={column.id}
                                                    className="capitalize"
                                                    checked={column.getIsVisible()}
                                                    onCheckedChange={(value) => column.toggleVisibility(!!value)}
                                                >
                                                    {column.id}
                                                </DropdownMenuCheckboxItem>
                                            )
                                        })}
                                </DropdownMenuContent>
                            </DropdownMenu>
                        )}
                    </div>
                </div>
            )}

            {hasSelectAllBanner && (
                <div className="p-3 bg-primary/10 border border-primary/20 rounded-lg flex items-center justify-between mb-4 animate-in fade-in slide-in-from-top-2 duration-300">
                    <span className="text-sm text-foreground">
                        All {table.getRowModel().rows.length} items on this page are selected.
                    </span>
                    <Button
                        variant="link"
                        size="sm"
                        className="text-primary h-auto p-0 font-semibold"
                        onClick={onSelectAllItems}
                    >
                        Select all {totalCount} items
                    </Button>
                </div>
            )}

            {hasAllSelectedBanner && (
                <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg flex items-center justify-between mb-4 animate-in fade-in slide-in-from-top-2 duration-300">
                    <span className="text-sm text-foreground">
                        All {totalCount} items are selected.
                    </span>
                    <Button
                        variant="link"
                        size="sm"
                        className="text-muted-foreground h-auto p-0"
                        onClick={() => {
                            table.resetRowSelection()
                            onClearSelection?.()
                        }}
                    >
                        Clear selection
                    </Button>
                </div>
            )}

            <div className={cn(
                "overflow-auto flex-1 min-h-0",
                !hideBorder && "border",
                !hideRounding && "rounded-md",
                "bg-card",
                containerClassName
            )}>
                <Table>
                    <TableHeader className="sticky top-0 bg-card z-10 shadow-sm">
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <TableHead key={header.id} className="bg-card">
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                    header.column.columnDef.header,
                                                    header.getContext()
                                                )}
                                        </TableHead>
                                    )
                                })}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => (
                                <TableRow
                                    key={row.id}
                                    data-state={row.getIsSelected() && "selected"}
                                    className={cn(enableRowSelectionOnClick && "cursor-pointer hover:bg-muted/50 select-none")}
                                    onClick={() => enableRowSelectionOnClick && row.toggleSelected()}
                                >
                                    {row.getVisibleCells().map((cell) => (
                                        <TableCell
                                            key={cell.id}
                                            onClick={(e) => {
                                                if (cell.column.id === "select" || cell.column.id === "actions") {
                                                    e.stopPropagation()
                                                }
                                            }}
                                        >
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={columns.length} className="h-24 text-center">
                                    No results.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            {!hidePagination && (
                <div className="flex items-center justify-between px-2 pt-4">
                    <div className="flex-1 text-sm text-muted-foreground">
                        {table.getFilteredSelectedRowModel().rows.length} of{" "}
                        {table.getFilteredRowModel().rows.length} row(s) selected.
                    </div>
                    <div className="flex items-center space-x-6 lg:space-x-8">
                        <div className="flex items-center space-x-2">
                            <p className="text-sm font-medium">Rows per page</p>
                            <select
                                className="h-8 w-[70px] rounded-md border border-input bg-transparent px-2 py-1 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                                value={table.getState().pagination.pageSize}
                                onChange={(e) => {
                                    table.setPageSize(Number(e.target.value))
                                }}
                            >
                                {[10, 20, 30, 40, 50].map((pageSize) => (
                                    <option key={pageSize} value={pageSize}>
                                        {pageSize}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="flex w-[100px] items-center justify-center text-sm font-medium">
                            Page {table.getState().pagination.pageIndex + 1} of{" "}
                            {table.getPageCount()}
                        </div>
                        <div className="flex items-center space-x-2">
                            <Button
                                variant="outline"
                                className="hidden h-8 w-8 p-0 lg:flex"
                                onClick={() => table.setPageIndex(0)}
                                disabled={!table.getCanPreviousPage()}
                            >
                                <span className="sr-only">Go to first page</span>
                                <ChevronsLeft className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="outline"
                                className="h-8 w-8 p-0"
                                onClick={() => table.previousPage()}
                                disabled={!table.getCanPreviousPage()}
                            >
                                <span className="sr-only">Go to previous page</span>
                                <ChevronLeft className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="outline"
                                className="h-8 w-8 p-0"
                                onClick={() => table.nextPage()}
                                disabled={!table.getCanNextPage()}
                            >
                                <span className="sr-only">Go to next page</span>
                                <ChevronRight className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="outline"
                                className="hidden h-8 w-8 p-0 lg:flex"
                                onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                                disabled={!table.getCanNextPage()}
                            >
                                <span className="sr-only">Go to last page</span>
                                <ChevronsRight className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
