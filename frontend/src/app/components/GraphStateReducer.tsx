import { Paper } from "../models/dbStructs";
import { GraphTicket } from "./GraphTicket";

export interface GraphPageState {
  tickets?: GraphTicket[];
  searchFrom?: number;
  searchTo?: number;
  contextFrom?: number;
  contextTo?: number;
  month?: number;
  grouping: "year" | "month";
  smoothing: number;
  selectedTicket?: number;
  source: "presse" | "livres" | "lemonde";
  linkTerm?: string;
}
export interface AddPaperAction {
  type: "add_paper";
  payload: Paper;
}

export interface RemovePaperAction {
  type: "remove_paper";
  payload: Paper["code"];
}

export interface AddTicketAction {
  type: "add_ticket";
  payload: GraphTicket;
}

export interface RemoveTicketAction {
  type: "remove_ticket";
  payload: GraphPageState["selectedTicket"];
}

export interface RemoveExampleTicketsAction {
  type: "remove_example_tickets";
}

export interface SetSearchFromAction {
  type: "set_search_from";
  payload: GraphPageState["searchFrom"];
}

export interface SetSearchToAction {
  type: "set_search_to";
  payload: GraphPageState["searchTo"];
}

export interface SetContextFromAction {
  type: "set_context_from";
  payload: GraphPageState["contextFrom"];
}

export interface SetContextToAction {
  type: "set_context_to";
  payload: GraphPageState["contextTo"];
}

export interface SetMonthAction {
  type: "set_month";
  payload: GraphPageState["month"];
}

export interface SetGroupingAction {
  type: "set_grouping";
  payload: GraphPageState["grouping"];
}

export interface SetSmoothingAction {
  type: "set_smoothing";
  payload: GraphPageState["smoothing"];
}

export interface SetSelectedTicketAction {
  type: "set_selected_ticket";
  payload: GraphPageState["selectedTicket"];
}

export interface SetLinkTermAction {
  type: "set_link_term";
  payload: GraphPageState["linkTerm"];
}

export interface SetSource {
  type: "set_source";
  payload: GraphPageState["source"];
}

export function graphStateReducer(
  state: GraphPageState,
  action:
    | AddTicketAction
    | RemoveTicketAction
    | SetMonthAction
    | SetGroupingAction
    | SetSmoothingAction
    | SetSelectedTicketAction
    | RemoveExampleTicketsAction
    | SetSearchFromAction
    | SetSearchToAction
    | SetSource
    | SetLinkTermAction
): GraphPageState {
  switch (action.type) {
    case "add_ticket":
      return {
        ...state,
        tickets: state.tickets
          ? [
              ...state.tickets.filter((ticket) => !ticket.example),
              action.payload,
            ]
          : [action.payload],
      };
    case "remove_ticket":
      return {
        ...state,
        tickets: state.tickets?.filter(
          (ticket) => ticket.id !== action.payload
        ),
      };
    case "set_month":
      return {
        ...state,
        month: action.payload,
      };
    case "set_grouping":
      return {
        ...state,
        grouping: action.payload,
      };
    case "set_smoothing":
      return {
        ...state,
        smoothing: action.payload,
      };
    case "set_selected_ticket":
      return {
        ...state,
        selectedTicket: action.payload,
      };
    case "remove_example_tickets":
      return {
        ...state,
        tickets: state.tickets?.filter((ticket) => !ticket.example),
      };
    case "set_search_from":
      return {
        ...state,
        searchFrom: action.payload,
      };
    case "set_search_to":
      return {
        ...state,
        searchTo: action.payload,
      };
    case "set_source":
      return {
        ...state,
        source: action.payload,
      };
    case "set_link_term":
      return {
        ...state,
        linkTerm: action.payload,
      };
  }
}
