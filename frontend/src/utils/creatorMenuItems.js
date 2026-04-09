import {
  ArrowRightLeft,
  Banknote,
  LayoutDashboard,
  MessageSquare,
  PiggyBank,
  UserCog,
  UserPen,
  Users,
} from "lucide-react";

export const menuItems = [
  {
    icon: LayoutDashboard,
    label: "Overview",
    path: "/creator-dashboard",
  },
  {
    icon: Users,
    label: "Supporters",
    path: "/creator-dashboard/supporters",
  },
  {
    icon: ArrowRightLeft,
    label: "Transactions",
    path: "/creator-dashboard/transactions",
  },
  {
    icon: Banknote,
    label: "Funds & Payouts",
    path: "/creator-dashboard/funds-and-payouts",
  },
  {
    icon: PiggyBank,
    label: "Payout Account",
    path: "/creator-dashboard/payout-account",
  },
  {
    icon: UserPen,
    label: "Edit Profile",
    path: "/creator-dashboard/edit-profile",
  },
  {
    icon: UserCog,
    label: "Guide",
    path: "/creator-dashboard/guide",
  },
  {
    icon: MessageSquare,
    label: "Talk to us",
    path: "#feedback",
    isAction: true,
  },
];

