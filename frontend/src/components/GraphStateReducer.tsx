import { GraphTicket } from "../pages/GraphTicket";
import {
  AddTicketAction,
  RemoveTicketAction,
  SetYearRangeAction,
  SetMonthAction,
  SetGroupingAction,
  SetSmoothingAction,
  SetSelectedTicketAction,
  RemoveExampleTicketsAction,
} from "./reducerActions";

export interface GraphPageState {
  tickets: GraphTicket[];
  yearRange: [number, number];
  month?: number;
  grouping: "year" | "month";
  smoothing: number;
  selectedTicket?: number;
}

export function graphStateReducer(
  state: GraphPageState,
  action:
    | AddTicketAction
    | RemoveTicketAction
    | SetYearRangeAction
    | SetMonthAction
    | SetGroupingAction
    | SetSmoothingAction
    | SetSelectedTicketAction
    | RemoveExampleTicketsAction
): GraphPageState {
  switch (action.type) {
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
        tickets: state.tickets.filter((ticket) => !ticket.example),
      };
  }
}
