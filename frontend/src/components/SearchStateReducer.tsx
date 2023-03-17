import { Paper } from "../models/dbStructs";
import { SearchTicket } from "../pages/index";

export interface SearchPageState {
  papers: Paper[];
  tickets: SearchTicket[];
  selectedTicket?: number;
  source: "book" | "periodical" | "all";
  limit: number;
  cursor: number;
  yearRange: [number | undefined, number | undefined];
  sort: "date" | "relevance";
  linkTerm?: string;
  linkDistance?: number;
}
export interface AddPaperAction {
  type: "add_paper";
  payload: Paper;
}

export interface RemovePaperAction {
  type: "remove_paper";
  payload: Paper["code"];
}

export interface SetSourceAction {
  type: "set_source";
  payload: SearchPageState["source"];
}

export interface SetLimitAction {
  type: "set_limit";
  payload: SearchPageState["limit"];
}

export interface SetCursorAction {
  type: "set_cursor";
  payload: SearchPageState["cursor"];
}

export interface AddTicketAction {
  type: "add_ticket";
  payload: SearchTicket;
}

export interface RemoveTicketAction {
  type: "remove_ticket";
  payload: SearchPageState["selectedTicket"];
}

export interface SetYearRangeAction {
  type: "set_year_range";
  payload: SearchPageState["yearRange"];
}

export interface SetSortAction {
  type: "set_sort";
  payload: SearchPageState["sort"];
}

export interface SetLinkTermAction {
  type: "set_link_term";
  payload: SearchPageState["linkTerm"];
}

export interface SetLinkDistanceAction {
  type: "set_link_distance";
  payload: SearchPageState["linkDistance"];
}

export function searchStateReducer(
  state: SearchPageState,
  action:
    | AddPaperAction
    | RemovePaperAction
    | SetSourceAction
    | SetLimitAction
    | SetCursorAction
    | AddTicketAction
    | RemoveTicketAction
    | SetYearRangeAction
    | SetSortAction
    | SetLinkTermAction
    | SetLinkDistanceAction
): SearchPageState {
  switch (action.type) {
    case "add_paper":
      return {
        ...state,
        papers: [...state.papers, action.payload],
      };
    case "remove_paper":
      return {
        ...state,
        papers: state.papers.filter((p) => p.code !== action.payload),
      };
    case "set_source":
      return {
        ...state,
        source: action.payload,
      };
    case "set_limit":
      return {
        ...state,
        limit: action.payload,
      };
    case "set_cursor":
      return {
        ...state,
        cursor: action.payload,
      };
    case "add_ticket":
      return {
        ...state,
        tickets: [...state.tickets, action.payload],
      };
    case "remove_ticket":
      return {
        ...state,
        tickets: state.tickets.filter((ticket) => ticket.id !== action.payload),
      };
    case "set_year_range":
      return {
        ...state,
        yearRange: action.payload,
      };
    case "set_sort":
      return {
        ...state,
        sort: action.payload,
      };

    case "set_link_term":
      return {
        ...state,
        linkTerm: action.payload,
      };
    case "set_link_distance":
      return {
        ...state,
        linkDistance: action.payload,
      };
  }
}
