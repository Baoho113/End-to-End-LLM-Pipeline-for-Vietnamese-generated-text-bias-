'use client'

import React, { useEffect, useRef, useState } from 'react'
import {
  Archive,
  Edit3,
  Eye,
 FileText,
  LogOut,
  MoreHorizontal,
  PanelLeftClose,
  PanelLeftOpen,
  Pin,
  PinOff,
  Plus,
  Trash2,
} from 'lucide-react'

import { getInitials } from '@/lib/utils'

interface ConversationPreview {
  id: string
  title: string
  pinned: boolean
  archived?: boolean
  createdAt: string
  updatedAt: string
  _count: {
    chats: number
  }
}

interface SidebarProps {
  userName: string
  conversations: ConversationPreview[]
  archivedConversations: ConversationPreview[]
  activeConversationId: string | null
  onNewChat: () => void
  onSelectConversation: (conversationId: string) => void
  onRenameConversation: (
    conversationId: string,
    title: string,
  ) => Promise<void>
  onTogglePinConversation: (
    conversationId: string,
  ) => Promise<void>
  onArchiveConversation: (
    conversationId: string,
  ) => Promise<void>
  onUnarchiveConversation: (
    conversationId: string,
  ) => Promise<void>
  onDeleteConversation: (
    conversationId: string,
  ) => Promise<void>
  onLogout: () => void
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

function MenuItem({
  icon: Icon,
  label,
  onClick,
  danger,
}: {
  icon: React.ElementType
  label: string
  onClick: () => void
  danger?: boolean
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        `
          flex w-full items-center gap-2

          rounded-lg

          px-3 py-2

          text-[12px]
          font-medium

          transition-all duration-200
        `,
        danger
          ? `
              text-rose-300

              hover:bg-rose-500/10
              hover:text-rose-200
            `
          : `
              text-[#a8a8ba]

              hover:bg-white/[0.04]
              hover:text-white
            `,
      ].join(' ')}
    >
      <Icon size={13} />
      {label}
    </button>
  )
}

function ConversationRow({
  conversation,
  active,
  collapsed,
  onSelect,
  onMenuToggle,
  isMenuOpen,
  onRenameClick,
  onTogglePin,
  onArchive,
  onDelete,
  isRenaming,
  renameValue,
  setRenameValue,
  onSaveRename,
  onCancelRename,
  menuRef,
}: {
  conversation: ConversationPreview
  active: boolean
  collapsed?: boolean
  onSelect: () => void
  onMenuToggle: () => void
  isMenuOpen: boolean
  onRenameClick: () => void
  onTogglePin: () => void
  onArchive: () => void
  onDelete: () => void
  isRenaming: boolean
  renameValue: string
  setRenameValue: (value: string) => void
  onSaveRename: () => void
  onCancelRename: () => void
  menuRef: React.RefObject<HTMLDivElement>
}) {
  return (
    <div className="relative">
      <div
        className={[
          `
            group
            relative

            flex items-center gap-2

            rounded-xl

            px-2 py-2

            transition-all duration-200
          `,
          active
            ? `
                bg-white/[0.06]
                text-white
              `
            : `
                text-[#8b8b9e]

                hover:bg-white/[0.04]
                hover:text-[#d7d7e7]
              `,
          collapsed ? 'justify-center px-0' : '',
        ].join(' ')}
      >
        <button
          type="button"
          onClick={onSelect}
          className={[
            `
              flex min-w-0 flex-1 items-center gap-2
              text-left
            `,
            collapsed ? 'justify-center' : '',
          ].join(' ')}
        >
          <FileText
            size={14}
            className={[
              `
                flex-shrink-0
                transition-colors duration-200
              `,
              active
                ? 'text-indigo-400'
                : 'text-[#5c5c72] group-hover:text-[#8d8da3]',
            ].join(' ')}
          />

          {!collapsed && (
            <>
              <span className="truncate text-[13px]">
                {conversation.title || 'Untitled analysis'}
              </span>

              {conversation.pinned && (
                <Pin
                  size={10}
                  className="ml-auto text-indigo-400"
                />
              )}
            </>
          )}
        </button>

        {!collapsed && (
          <button
            type="button"
            onClick={e => {
              e.stopPropagation()
              onMenuToggle()
            }}
            aria-label="More options"
            className={[
              `
                flex h-7 w-7 items-center justify-center

                rounded-lg

                transition-all duration-200
              `,
              isMenuOpen
                ? `
                    bg-white/[0.05]
                    text-white
                    opacity-100
                  `
                : `
                    text-[#5c5c72]
                    opacity-0

                    hover:bg-white/[0.05]
                    hover:text-white

                    group-hover:opacity-100
                  `,
            ].join(' ')}
          >
            <MoreHorizontal size={14} />
          </button>
        )}
      </div>

      {/* Conversation Menu */}
      {isMenuOpen && !collapsed && (
        <div
          ref={menuRef}
          className="
            absolute
            left-2 right-2 top-full
            z-50
            mt-1

            rounded-2xl

            border border-white/[0.06]

            bg-[#101018]/95
            backdrop-blur-2xl

            p-1.5

            shadow-[0_20px_60px_rgba(0,0,0,0.45)]

            animate-in
            fade-in-0
            zoom-in-95
            duration-200
          "
        >
          {isRenaming ? (
            <div className="space-y-2 p-1">
              <input
                autoFocus
                value={renameValue}
                onChange={e =>
                  setRenameValue(e.target.value)
                }
                onKeyDown={e => {
                  if (e.key === 'Enter')
                    onSaveRename()

                  if (e.key === 'Escape')
                    onCancelRename()
                }}
                placeholder="Rename conversation..."
                className="
                  w-full

                  rounded-xl

                  border border-white/[0.06]
                  bg-white/[0.04]

                  px-3 py-2

                  text-[12px]
                  text-white

                  outline-none

                  placeholder:text-[#5f5f73]

                  focus:border-indigo-500/40
                "
              />

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={onSaveRename}
                  className="
                    flex-1

                    rounded-xl

                    bg-indigo-500

                    py-2

                    text-[12px]
                    font-medium
                    text-white

                    transition-colors duration-200

                    hover:bg-indigo-400
                  "
                >
                  Save
                </button>

                <button
                  type="button"
                  onClick={onCancelRename}
                  className="
                    flex-1

                    rounded-xl

                    border border-white/[0.06]
                    bg-white/[0.03]

                    py-2

                    text-[12px]
                    text-[#b8b8c7]

                    transition-colors duration-200

                    hover:bg-white/[0.05]
                  "
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <MenuItem
                icon={Edit3}
                label="Rename"
                onClick={onRenameClick}
              />

              <MenuItem
                icon={
                  conversation.pinned ? PinOff : Pin
                }
                label={
                  conversation.pinned
                    ? 'Unpin'
                    : 'Pin'
                }
                onClick={onTogglePin}
              />

              <MenuItem
                icon={Archive}
                label="Archive"
                onClick={onArchive}
              />

              <div className="my-1 border-t border-white/[0.05]" />

              <MenuItem
                icon={Trash2}
                label="Delete"
                onClick={onDelete}
                danger
              />
            </>
          )}
        </div>
      )}
    </div>
  )
}

export const Sidebar: React.FC<SidebarProps> = ({
  userName,
  conversations,
  archivedConversations,
  activeConversationId,
  onNewChat,
  onSelectConversation,
  onRenameConversation,
  onTogglePinConversation,
  onArchiveConversation,
  onUnarchiveConversation,
  onDeleteConversation,
  onLogout,
  open: controlledOpen,
  onOpenChange,
}) => {
  const [internalOpen, setInternalOpen] =
    useState(true)

  const [openMenuId, setOpenMenuId] = useState<
    string | null
  >(null)

  const [renamingId, setRenamingId] = useState<
    string | null
  >(null)

  const [renameValue, setRenameValue] =
    useState('')

  const [footerMenuOpen, setFooterMenuOpen] =
    useState(false)

  const [archiveModalOpen, setArchiveModalOpen] =
    useState(false)

  const sidebarRef =
    useRef<HTMLDivElement>(null) as React.MutableRefObject<HTMLDivElement | null>

  const menuRef =
    useRef<HTMLDivElement>(null) as React.MutableRefObject<HTMLDivElement | null>

  const footerMenuRef =
    useRef<HTMLDivElement>(null) as React.MutableRefObject<HTMLDivElement | null>

  const archiveModalRef =
    useRef<HTMLDivElement>(null) as React.MutableRefObject<HTMLDivElement | null>

  const isOpen =
    controlledOpen ?? internalOpen

  const initials = getInitials(userName)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      const target = e.target as Node

      const clickedMenu =
        menuRef.current?.contains(target)

      const clickedFooter =
        footerMenuRef.current?.contains(target)

      const clickedArchiveModal =
        archiveModalRef.current?.contains(target)

      if (!clickedMenu && !clickedFooter && !clickedArchiveModal) {
        setOpenMenuId(null)
        setRenamingId(null)
        setFooterMenuOpen(false)
        setArchiveModalOpen(false)
      }
    }

    document.addEventListener(
      'mousedown',
      handleClickOutside,
    )

    return () =>
      document.removeEventListener(
        'mousedown',
        handleClickOutside,
      )
  }, [])

  function toggleOpen() {
    const next = !isOpen

    setInternalOpen(next)

    onOpenChange?.(next)
  }

  const pinnedConvos = conversations.filter(
    c => c.pinned,
  )

  const unpinnedConvos = conversations.filter(
    c => !c.pinned,
  )

  const handleMenuToggle = (id: string) => {
    if (openMenuId === id) {
      setOpenMenuId(null)
      setRenamingId(null)
    } else {
      setOpenMenuId(id)
      setRenamingId(null)
    }
  }

  const handleRenameClick = (
    conv: ConversationPreview,
  ) => {
    setRenamingId(conv.id)
    setRenameValue(conv.title || '')
  }

  const handleSaveRename = async (
    id: string,
  ) => {
    const title = renameValue.trim()

    if (!title) return

    await onRenameConversation(id, title)

    setOpenMenuId(null)
    setRenamingId(null)
  }

  const handleSelect = async (id: string) => {
    await onSelectConversation(id)

    setOpenMenuId(null)
    setRenamingId(null)
  }

  const handleFooterToggle = () => {
    setFooterMenuOpen(prev => !prev)
    if (archiveModalOpen) {
      setArchiveModalOpen(false)
    }

    setOpenMenuId(null)
    setRenamingId(null)
  }

  const handleViewArchive = () => {
    setArchiveModalOpen(true)
    setFooterMenuOpen(false)
    setOpenMenuId(null)
    setRenamingId(null)
  }

  const handleCloseArchive = () => {
    setArchiveModalOpen(false)
  }

  return (
    <div
      ref={sidebarRef}
      className={[
        `
          relative
          flex-shrink-0

          border-r border-white/[0.05]

          bg-[#0b0b12]

          transition-all duration-300
          ease-[cubic-bezier(0.22,1,0.36,1)]

          will-change-[width]
        `,
        isOpen ? 'w-64' : 'w-[56px]',
      ].join(' ')}
    >
      <aside className="flex h-full flex-col">
        {/* Header */}
        <div
          className={[
            `
              flex h-14 items-center

              border-b border-white/[0.05]

              px-3
            `,
            isOpen
              ? 'justify-between'
              : 'justify-center',
          ].join(' ')}
        >
          {isOpen ? (
            <>
              <div className="flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-indigo-500 text-white shadow-lg shadow-indigo-500/20">
                  <Eye size={14} />
                </div>

                <div>
                  <p className="text-[13px] font-semibold text-white">
                    BiasLens
                  </p>

                  <p className="text-[10px] text-[#5f5f73]">
                    AI Analysis
                  </p>
                </div>
              </div>

              <button
                onClick={toggleOpen}
                className="
                  flex h-8 w-8 items-center justify-center

                  rounded-xl

                  text-[#5f5f73]

                  transition-all duration-200

                  hover:bg-white/[0.04]
                  hover:text-white
                "
              >
                <PanelLeftClose size={15} />
              </button>
            </>
          ) : (
            <button
              onClick={toggleOpen}
              className="
                flex h-9 w-9 items-center justify-center

                rounded-xl

                bg-indigo-500

                text-white

                shadow-lg shadow-indigo-500/20

                transition-transform duration-200

                hover:scale-105
              "
            >
              <PanelLeftOpen size={16} />
            </button>
          )}
        </div>

        {/* New Chat */}
        <div className="p-2">
          <button
            onClick={onNewChat}
            className={[
              `
                group
                flex items-center gap-2

                rounded-xl

                bg-white/[0.03]

                px-3 py-2.5

                text-[12px]
                font-medium
                text-[#b8b8c7]

                transition-all duration-200

                hover:bg-white/[0.06]
                hover:text-white
              `,
              isOpen
                ? 'justify-start'
                : 'justify-center px-0 h-9 w-9 rounded-xl bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 transition-transform duration-200 hover:scale-105',
            ].join(' ')}
          >
            <Plus
              size={isOpen ? 15 : 16}
              className="transition-transform duration-200 group-hover:rotate-90"
            />

            {isOpen && 'New analysis'}
          </button>
        </div>

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto px-2 pb-2">
          {pinnedConvos.length > 0 && isOpen && (
            <div className="mb-3">
              <p className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#4a4a5e]">
                Pinned
              </p>

              <div className="space-y-1">
                {pinnedConvos.map(conv => (
                  <ConversationRow
                    key={conv.id}
                    conversation={conv}
                    active={
                      activeConversationId === conv.id
                    }
                    collapsed={!isOpen}
                    onSelect={() =>
                      handleSelect(conv.id)
                    }
                    onMenuToggle={() =>
                      handleMenuToggle(conv.id)
                    }
                    isMenuOpen={
                      openMenuId === conv.id
                    }
                    onRenameClick={() =>
                      handleRenameClick(conv)
                    }
                    onTogglePin={() => {
                      onTogglePinConversation(
                        conv.id,
                      )

                      setOpenMenuId(null)
                    }}
                    onArchive={() => {
                      onArchiveConversation(
                        conv.id,
                      )

                      setOpenMenuId(null)
                    }}
                    onDelete={() => {
                      onDeleteConversation(
                        conv.id,
                      )

                      setOpenMenuId(null)
                    }}
                    isRenaming={
                      renamingId === conv.id
                    }
                    renameValue={renameValue}
                    setRenameValue={
                      setRenameValue
                    }
                    onSaveRename={() =>
                      handleSaveRename(conv.id)
                    }
                    onCancelRename={() =>
                      setRenamingId(null)
                    }
                    menuRef={menuRef}
                  />
                ))}
              </div>
            </div>
          )}

          {unpinnedConvos.length > 0 && (
            <div>
              {isOpen && (
                <p className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#4a4a5e]">
                  Recent
                </p>
              )}

              <div className="space-y-1">
                {unpinnedConvos.map(conv => (
                  <ConversationRow
                    key={conv.id}
                    conversation={conv}
                    active={
                      activeConversationId === conv.id
                    }
                    collapsed={!isOpen}
                    onSelect={() =>
                      handleSelect(conv.id)
                    }
                    onMenuToggle={() =>
                      handleMenuToggle(conv.id)
                    }
                    isMenuOpen={
                      openMenuId === conv.id
                    }
                    onRenameClick={() =>
                      handleRenameClick(conv)
                    }
                    onTogglePin={() => {
                      onTogglePinConversation(
                        conv.id,
                      )

                      setOpenMenuId(null)
                    }}
                    onArchive={() => {
                      onArchiveConversation(
                        conv.id,
                      )

                      setOpenMenuId(null)
                    }}
                    onDelete={() => {
                      onDeleteConversation(
                        conv.id,
                      )

                      setOpenMenuId(null)
                    }}
                    isRenaming={
                      renamingId === conv.id
                    }
                    renameValue={renameValue}
                    setRenameValue={
                      setRenameValue
                    }
                    onSaveRename={() =>
                      handleSaveRename(conv.id)
                    }
                    onCancelRename={() =>
                      setRenamingId(null)
                    }
                    menuRef={menuRef}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-white/[0.05] p-2">
          <button
            type="button"
            onClick={handleFooterToggle}
            className={[
              `
                group
                flex w-full items-center gap-3

                rounded-xl

                px-2 py-2

                transition-all duration-200

                hover:bg-white/[0.04]
              `,
              !isOpen
                ? 'justify-center px-0'
                : '',
            ].join(' ')}
          >
            <div
              className="
                flex h-8 w-8 items-center justify-center

                rounded-full

                bg-indigo-500/15

                text-[10px]
                font-semibold
                text-indigo-300

                ring-1 ring-white/[0.05]
              "
            >
              {initials}
            </div>

            {isOpen && (
              <>
                <div className="min-w-0 flex-1 text-left">
                  <p className="truncate text-[12px] font-medium text-[#d7d7e7]">
                    {userName}
                  </p>
                </div>

                <MoreHorizontal
                  size={14}
                  className="
                    text-[#5f5f73]

                    transition-colors duration-200

                    group-hover:text-[#b8b8c7]
                  "
                />
              </>
            )}
          </button>
        </div>

        {/* Floating Footer Menu */}
        {footerMenuOpen && (
          <div className="relative">
            <div
              ref={footerMenuRef}
              className={[
                `
                  absolute
                  bottom-[68px]
                  z-[100]

                  rounded-2xl

                  border border-white/[0.06]

                  bg-[#101018]/95
                  backdrop-blur-2xl

                  shadow-[0_20px_80px_rgba(0,0,0,0.45)]

                  overflow-hidden

                  animate-in

                  fade-in-0

                  zoom-in-95

                  duration-200
                `,
                isOpen
                  ? 'left-2 w-[280px]'
                  : 'left-14 w-[280px]',
              ].join(' ')}
            >
              <div className="flex items-center gap-3 border-b border-white/[0.05] px-4 py-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-500/15 text-[12px] font-semibold text-indigo-300">
                  {initials}
                </div>

                <div className="min-w-0 flex-1">
                  <p className="truncate text-[13px] font-medium text-white">
                    {userName}
                  </p>

                  <p className="text-[11px] text-[#6b6b7e]">
                    Beta Test
                  </p>
                </div>
              </div>

              <div className="px-4 py-4">
                <button
                  type="button"
                  onClick={handleViewArchive}
                  className="
                    flex w-full items-center justify-between
                    rounded-xl
                    border border-white/[0.06]
                    bg-white/[0.03]
                    px-3 py-2.5
                    text-[12px]
                    font-medium
                    text-[#c9c9d8]
                    transition-all duration-200
                    hover:bg-white/[0.06]
                    hover:text-white
                  "
                >
                  <span>View archive</span>
                  <span className="text-[#6b6b7e]">→</span>
                </button>
              </div>

              <div className="border-t border-white/[0.05] p-2">
                <button
                  type="button"
                  onClick={() => {
                    setFooterMenuOpen(false)
                    setArchiveModalOpen(false)
                    onLogout()
                  }}
                  className="
                    flex w-full items-center gap-2
                    rounded-xl
                    px-3 py-2.5
                    text-[12px]
                    font-medium
                    text-rose-300
                    transition-all duration-200
                    hover:bg-rose-500/10
                    hover:text-rose-200
                  "
                >
                  <LogOut size={14} />
                  Log out
                </button>
              </div>
            </div>
          </div>
        )}
      </aside>

      {archiveModalOpen && (
        <div className="fixed inset-0 z-[120] flex items-center justify-center bg-black/40 backdrop-blur-sm px-4 py-6">
          <div
            ref={archiveModalRef}
            className="w-full max-w-[420px] overflow-hidden rounded-[32px] border border-white/[0.08] bg-[#101018]/95 shadow-[0_20px_80px_rgba(0,0,0,0.45)]"
          >
            <div className="flex items-center justify-between gap-3 border-b border-white/[0.05] px-5 py-4">
              <div>
                <p className="text-[15px] font-semibold text-white">
                  Archived Conversations
                </p>
                <p className="text-[11px] text-[#8a8aa3]">
                  Review and restore saved chats
                </p>
              </div>
              <button
                type="button"
                onClick={handleCloseArchive}
                className="text-[#6b6b7e] transition-colors duration-200 hover:text-white"
              >
                ×
              </button>
            </div>

            <div className="max-h-[calc(100vh-220px)] overflow-y-auto px-5 py-4">
              {archivedConversations.length === 0 ? (
                <div className="px-2 py-8 text-center text-[12px] text-[#7b7b8d]">
                  No archived chats
                </div>
              ) : (
                <div className="space-y-2">
                  {archivedConversations.map(conv => (
                    <div
                      key={conv.id}
                      className="flex items-center gap-3 rounded-3xl border border-white/[0.05] bg-white/[0.03] px-4 py-3"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-[13px] font-medium text-white">
                          {conv.title || 'Untitled analysis'}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          onUnarchiveConversation(conv.id)
                          handleCloseArchive()
                        }}
                        className="rounded-full bg-indigo-500 px-3 py-1.5 text-[12px] font-medium text-white transition-colors duration-200 hover:bg-indigo-400"
                      >
                        Restore
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Sidebar