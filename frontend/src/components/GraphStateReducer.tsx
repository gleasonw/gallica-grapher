import { Paper } from "../models/dbStructs";
import { GraphTicket } from "./GraphTicket";

export interface GraphPageState {
  tickets?: GraphTicket[];
  contextYearRange: [number | undefined, number | undefined];
  searchYearRange: [number | undefined, number | undefined];
  month?: number;
  grouping: "year" | "month";
  smoothing: number;
  selectedTicket?: number;
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

export interface SetContextYearRangeAction {
  type: "set_context_range";
  payload: GraphPageState["contextYearRange"];
}

export interface SetSearchYearRangeAction {
  type: "set_search_range";
  payload: GraphPageState["contextYearRange"];
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
export function graphStateReducer(
  state: GraphPageState,
  action:
    | AddTicketAction
    | RemoveTicketAction
    | SetContextYearRangeAction
    | SetMonthAction
    | SetGroupingAction
    | SetSmoothingAction
    | SetSelectedTicketAction
    | RemoveExampleTicketsAction
    | SetSearchYearRangeAction
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
    case "set_context_range":
      return {
        ...state,
        contextYearRange: action.payload,
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
    case "set_search_range":
      return {
        ...state,
        searchYearRange: action.payload,
      };
  }
}
